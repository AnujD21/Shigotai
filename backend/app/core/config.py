from functools import lru_cache

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


_INSECURE_DEFAULT_SECRET = "dev-only-insecure-secret-change-me"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"
    demo_mode: bool = True

    auth_secret: str = _INSECURE_DEFAULT_SECRET
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30
    jwt_algorithm: str = "HS256"

    database_url: str = "sqlite:///./shigotai.db"
    redis_url: str = ""

    # dev (rule-based, offline) | anthropic | groq | gemini | openrouter |
    # openai_compatible (any OpenAI-style endpoint via LLM_BASE_URL)
    llm_provider: str = "dev"
    llm_api_key: str = ""
    # Required for groq/gemini/openrouter (copy the model ID from the
    # provider's console); defaults to claude-opus-5-5 for anthropic.
    llm_model: str = ""
    llm_base_url: str = ""
    # Minimum spacing between LLM calls -- set ~2.5 for batch ingestion on a
    # free tier capped at ~30 requests/minute.
    llm_min_interval_seconds: float = 0.0
    # Optional separate provider for resume parsing (personal data). Empty =
    # reuse the main LLM provider.
    resume_llm_provider: str = ""
    resume_llm_api_key: str = ""
    resume_llm_model: str = ""
    resume_llm_base_url: str = ""
    # LLM-written match explanations per recompute; the rest get the instant
    # rule-based explanation so a recompute over hundreds of jobs can't blow
    # through a request timeout or a free-tier rate limit.
    max_llm_explanations_per_recompute: int = 8

    # dev (writes to backend/var/outbox) | resend | smtp
    email_provider: str = "dev"
    email_api_key: str = ""
    email_from: str = "notifications@shigotai.app"
    # SMTP works with a Gmail app password or Brevo's free SMTP relay, so
    # emails reach real users without owning a domain.
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""

    web_push_public_key: str = ""
    web_push_private_key: str = ""
    web_push_subject: str = "mailto:support@shigotai.app"

    # "dev" writes uploads to backend/var/ on local disk. On hosts with an
    # ephemeral/read-only filesystem (Vercel, most PaaS) use "none" -- the
    # resume is parsed and discarded, only its filename is kept -- or "s3"
    # for AWS S3 or any S3-compatible store (Cloudflare R2, Backblaze B2,
    # MinIO) by pointing STORAGE_ENDPOINT_URL at it.
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

    @model_validator(mode="after")
    def _require_real_secret_in_production(self) -> "Settings":
        # Anyone who knows the default secret can mint login tokens for any
        # account, so refuse to boot a production deployment with it.
        if self.environment == "production" and self.auth_secret == _INSECURE_DEFAULT_SECRET:
            raise ValueError("AUTH_SECRET must be set to a long random value when ENVIRONMENT=production")
        return self

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
