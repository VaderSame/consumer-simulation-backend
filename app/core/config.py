from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Consumer AI Simulation API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Frontend
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "https://1wv81v92-5173.use.devtunnels.ms",
        
    ]
   

    # ------------------------------------------------------------------
    # LLM configuration
    # ------------------------------------------------------------------
    # ollama | openrouter | anthropic
    LLM_PROVIDER: str = "ollama"

    # Keep responses controlled and short for the experiment.
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 350

    # Local development
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL: str = "qwen3:8b"

    # OpenRouter no longer serves qwen/qwen3-8b. qwen/qwen3.5-9b is the closest live model.
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "qwen/qwen3.5-9b"

    # Final study provider
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
