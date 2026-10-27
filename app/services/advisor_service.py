import time
from collections.abc import AsyncIterator
from typing import Iterable

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from app.llm.prompt_builder import build_system_prompt
from app.llm.provider import get_chat_model
from app.models.schemas import Condition, Trial

# Track recent warm-ups so we don't spam duplicate prefill pings within 45s
_LAST_WARMUP: dict[tuple[str, str], float] = {}
_WARMUP_COOLDOWN_SEC = 45.0


def _text_from_content(content: object, *, strip: bool = True) -> str:
    if isinstance(content, str):
        return content.strip() if strip else content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                text = block.get("text") or block.get("content") or ""
                if text:
                    parts.append(str(text))
        joined = "".join(parts) if not strip else "\n".join(p.strip() for p in parts if p and p.strip())
        return joined.strip() if strip else joined
    text = str(content)
    return text.strip() if strip else text


def _build_messages(
    *,
    trial: Trial,
    condition: Condition,
    user_message: str,
    history: Iterable[dict] | None = None,
    active_stage: str | None = None,
) -> list[BaseMessage]:
    system_prompt = build_system_prompt(
        trial=trial,
        condition=condition,
        active_stage=active_stage,
    )

    messages: list[BaseMessage] = [SystemMessage(content=system_prompt)]
    for turn in history or []:
        role = str(turn.get("role", "")).lower()
        text = str(turn.get("content") or turn.get("text") or "").strip()
        if not text:
            continue
        if role in {"user", "human"}:
            messages.append(HumanMessage(content=text))
        elif role in {"assistant", "advisor", "ai"}:
            messages.append(AIMessage(content=text))

    messages.append(HumanMessage(content=user_message.strip()))
    return messages


async def warm_advisor_cache(
    *,
    trial: Trial,
    condition: Condition,
) -> None:
    """
    Silently pre-warms the TLS socket and GPU prefix KV-cache for (trial, condition)
    while the participant is reading the scenario, so their first question streams fast.
    """
    if condition == Condition.CONTROL:
        return

    key = (trial.trial_id, condition.value)
    now = time.monotonic()
    if now - _LAST_WARMUP.get(key, 0.0) < _WARMUP_COOLDOWN_SEC:
        return
    _LAST_WARMUP[key] = now

    try:
        model = get_chat_model()
        active_stage = "clarify" if condition == Condition.AI_STRUCTURED else None
        system_prompt = build_system_prompt(
            trial=trial,
            condition=condition,
            active_stage=active_stage,
        )
        messages: list[BaseMessage] = [
            SystemMessage(content=system_prompt),
            HumanMessage(content="Ready?"),
        ]
        await model.bind(max_tokens=1).ainvoke(messages)
    except Exception:
        # Never surface background warm-up errors to the participant
        _LAST_WARMUP.pop(key, None)


async def generate_advisor_response(
    *,
    trial: Trial,
    condition: Condition,
    user_message: str,
    history: Iterable[dict] | None = None,
    active_stage: str | None = None,
) -> str:
    """
    Generate one live follow-up response (full text).

    The scripted opening is not generated here.
    It remains controlled by the trial configuration.
    """
    model = get_chat_model()
    messages = _build_messages(
        trial=trial,
        condition=condition,
        user_message=user_message,
        history=history,
        active_stage=active_stage,
    )
    response = await model.ainvoke(messages)
    return _text_from_content(response.content, strip=True)


async def stream_advisor_response(
    *,
    trial: Trial,
    condition: Condition,
    user_message: str,
    history: Iterable[dict] | None = None,
    active_stage: str | None = None,
) -> AsyncIterator[str]:
    """
    Stream live follow-up response token-by-token for immediate UI rendering.
    """
    model = get_chat_model()
    messages = _build_messages(
        trial=trial,
        condition=condition,
        user_message=user_message,
        history=history,
        active_stage=active_stage,
    )
    async for chunk in model.astream(messages):
        piece = _text_from_content(chunk.content, strip=False)
        if piece:
            yield piece
