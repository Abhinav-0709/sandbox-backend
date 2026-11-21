from functools import lru_cache
from pathlib import Path
from typing import List
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[
            _BACKEND_DIR / ".env",
            ".env",
        ],
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "Vivoki Sandbox Microservice"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8001
    LOG_LEVEL: str = "info"
    API_PREFIX: str = "/api/v1/sandbox"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/postgres"

    # Supabase Auth
    SUPABASE_URL: str = "https://shxftvabqhfmknachbhb.supabase.co"
    SUPABASE_JWT_SECRET: str = ""
    ENABLE_DEV_AUTH: bool = True

    # CORS
    ALLOWED_ORIGINS: str = (
        "http://localhost:3000,http://localhost:3001,http://localhost:3005,https://vivoki.ai,https://www.vivoki.ai"
    )

    # AI / LLM Assisted Evaluation
    AI_EVALUATION_ENABLED: bool = True
    AI_PROVIDER: str = "gemini"  # "gemini" | "openai" | "groq" | "mock"
    AI_API_KEY: str = ""
    AI_MODEL: str = "gemini-1.5-flash"
    AI_BASE_URL: str = ""
    AI_TIMEOUT_SECONDS: float = 8.0

    @computed_field
    @property
    def cors_origins(self) -> List[str]:
        configured = [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
        defaults = [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:3005",
            "https://vivoki.ai",
            "https://www.vivoki.ai",
        ]
        for d in defaults:
            if d not in configured:
                configured.append(d)
        return configured

    @computed_field
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    @computed_field
    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT.lower() == "test"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
