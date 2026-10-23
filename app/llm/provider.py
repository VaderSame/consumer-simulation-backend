from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama

from app.core.config import settings


def get_model_name() -> str:
    """Name recorded with each reply so a session can be tied to a model version."""
    provider = settings.LLM_PROVIDER.strip().lower()
    if provider == "anthropic":
        return settings.ANTHROPIC_MODEL or "claude-sonnet-4-5"
    if provider == "openrouter":
        return settings.OPENROUTER_MODEL
    return settings.OLLAMA_MODEL


def get_chat_model() -> BaseChatModel:
    """
    Returns the configured chat model.

    Development:
        Ollama -> qwen3:8b
        OpenRouter -> qwen/qwen3.5-9b
    Final experiment:
        Anthropic -> Claude

    The rest of the application should not need to know which
    provider is being used.
    """
    provider = settings.LLM_PROVIDER.strip().lower()

    if provider == "ollama":
        return ChatOllama(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=settings.LLM_TEMPERATURE,
            num_predict=settings.LLM_MAX_TOKENS,
            # Qwen3 defaults to thinking mode.
            # Participant-facing responses should contain only the answer.
            reasoning=False,
        )

    if provider == "openrouter":
        if not settings.OPENROUTER_API_KEY:
            raise RuntimeError(
                "LLM_PROVIDER is 'openrouter' but OPENROUTER_API_KEY is not set."
            )
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.OPENROUTER_MODEL,
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
            # Qwen3 thinking traces must not reach the participant.
            extra_body={"reasoning": {"enabled": False}},
        )

    if provider == "anthropic":
        if not settings.ANTHROPIC_API_KEY:
            raise RuntimeError(
                "LLM_PROVIDER is 'anthropic' but ANTHROPIC_API_KEY is not set."
            )
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model_name=settings.ANTHROPIC_MODEL or "claude-sonnet-4-5",
            api_key=settings.ANTHROPIC_API_KEY,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )

    raise ValueError(
        f"Unsupported LLM_PROVIDER '{settings.LLM_PROVIDER}'. Use 'ollama', 'openrouter', or 'anthropic'."
    )
