from functools import lru_cache

from app.ai.base import LLMProvider
from app.ai.dev_provider import DevLLMProvider
from app.core.config import get_settings


@lru_cache
def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    if settings.llm_provider == "anthropic" and settings.llm_api_key:
        from app.ai.anthropic_provider import AnthropicLLMProvider

        return AnthropicLLMProvider(settings.llm_api_key, settings.llm_model)
    return DevLLMProvider()
