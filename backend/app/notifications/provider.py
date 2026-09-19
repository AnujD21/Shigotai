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
    return DevEmailProvider()
