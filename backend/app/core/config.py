from functools import lru_cache

from pydantic import field_validator
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

    # "dev" writes uploads to backend/var/ on local disk. Set to "s3" in any
    # environment with an ephemeral/read-only filesystem (most PaaS hosts) --
    # works with AWS S3 or any S3-compatible store (Cloudflare R2, Backblaze
    # B2, MinIO) by pointing STORAGE_ENDPOINT_URL at it.
    storage_provider: str = "dev"
    storage_bucket: str = ""
    storage_region: str = "auto"
    storage_access_key_id: str = ""
    storage_secret_access_key: str = ""
    storage_endpoint_url: str = ""
    storage_public_base_url: str = ""

    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Used to build links in outgoing emails (verify-email, password reset,
    # match notifications). Must be the real deployed frontend URL in
    # production -- these links are wrong otherwise.
    frontend_base_url: str = "http://localhost:3000"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: object) -> object:
        # Lets CORS_ORIGINS be set as a plain comma-separated string in a
        # platform's env var UI (e.g. "https://app.example.com,https://example.com")
        # instead of requiring JSON-list syntax.
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
