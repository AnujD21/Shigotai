from functools import lru_cache

from app.core.config import get_settings
from app.notifications.base import EmailProvider
from app.notifications.dev_providers import DevEmailProvider


@lru_cache
def get_email_provider() -> EmailProvider:
    settings = get_settings()
    if settings.email_provider == "resend" and settings.email_api_key:
        from app.notifications.resend_provider import ResendEmailProvider

        return ResendEmailProvider(settings.email_api_key, settings.email_from)
    if settings.email_provider == "smtp" and settings.smtp_host:
        from app.notifications.smtp_provider import SMTPEmailProvider

        return SMTPEmailProvider(
            settings.smtp_host,
            settings.smtp_port,
            settings.smtp_username,
            settings.smtp_password,
            settings.email_from,
        )
    return DevEmailProvider()
