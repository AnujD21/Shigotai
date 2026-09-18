from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"
    demo_mode: bool = True

    auth_secret: str = "dev-only-insecure-secret-change-me"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30
    jwt_algorithm: str = "HS256"

    database_url: str = "sqlite:///./shigotai.db"
    redis_url: str = ""

    llm_provider: str = "dev"
    llm_api_key: str = ""
    llm_model: str = "claude-sonnet-5"

    email_provider: str = "dev"
    email_api_key: str = ""
    email_from: str = "notifications@shigotai.app"

    web_push_public_key: str = ""
    web_push_private_key: str = ""
    web_push_subject: str = "mailto:support@shigotai.app"

    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
