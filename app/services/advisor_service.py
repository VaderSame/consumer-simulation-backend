from typing import Iterable

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.llm.prompt_builder import build_system_prompt
from app.llm.provider import get_chat_model
from app.models.schemas import Condition, Trial


def _text_from_content(content: object) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                text = block.get("text") or block.get("content") or ""
                if text:
                    parts.append(str(text))
        return "\n".join(part.strip() for part in parts if part and part.strip()).strip()
    return str(content).strip()


async def generate_advisor_response(
    *,
    trial: Trial,
    condition: Condition,
    user_message: str,
    history: Iterable[dict] | None = None,
    active_stage: str | None = None,
) -> str:
    """
    Generate one live follow-up response.

    The scripted opening is not generated here.
    It remains controlled by the trial configuration.
    """
    model = get_chat_model()
    system_prompt = build_system_prompt(
        trial=trial,
        condition=condition,
        active_stage=active_stage,
    )

    messages = [SystemMessage(content=system_prompt)]
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
    response = await model.ainvoke(messages)
    return _text_from_content(response.content)
