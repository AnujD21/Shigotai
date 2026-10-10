import logging
from functools import lru_cache

from app.ai.base import LLMProvider
from app.ai.dev_provider import DevLLMProvider
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Free-tier-friendly endpoints that speak the OpenAI chat-completions protocol.
OPENAI_COMPATIBLE_PRESETS = {
    "groq": "https://api.groq.com/openai/v1",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai",
    "openrouter": "https://openrouter.ai/api/v1",
}
_DEFAULT_ANTHROPIC_MODEL = "claude-opus-5-5"


def _build_provider(kind: str, api_key: str, model: str, base_url: str, min_interval: float) -> LLMProvider:
    kind = kind.strip().lower()
    if kind in ("", "dev") or not api_key:
        if kind not in ("", "dev"):
            logger.warning("LLM provider %r configured without an API key; using rule-based extraction", kind)
        return DevLLMProvider()

    if kind == "anthropic":
        from app.ai.anthropic_provider import AnthropicLLMProvider

        return AnthropicLLMProvider(api_key, model or _DEFAULT_ANTHROPIC_MODEL)

    url = base_url or OPENAI_COMPATIBLE_PRESETS.get(kind, "")
    if not url or not model:
        logger.warning(
            "LLM provider %r needs LLM_MODEL%s; using rule-based extraction",
            kind,
            "" if kind in OPENAI_COMPATIBLE_PRESETS else " and LLM_BASE_URL",
        )
        return DevLLMProvider()

    from app.ai.openai_compat_provider import OpenAICompatibleLLMProvider

    return OpenAICompatibleLLMProvider(url, api_key, model, min_interval)


@lru_cache
def get_llm_provider() -> LLMProvider:
    """Provider for job-posting extraction and match explanations."""
    s = get_settings()
    return _build_provider(s.llm_provider, s.llm_api_key, s.llm_model, s.llm_base_url, s.llm_min_interval_seconds)


@lru_cache
def get_resume_llm_provider() -> LLMProvider:
    """Provider for resume parsing.

    Resumes are personal data while job postings are public, so this can
    point at a different provider (e.g. one that doesn't train on inputs)
    via RESUME_LLM_*; unset, it reuses the main provider.
    """
    s = get_settings()
    if not s.resume_llm_provider:
        return get_llm_provider()
    return _build_provider(
        s.resume_llm_provider,
        s.resume_llm_api_key,
        s.resume_llm_model,
        s.resume_llm_base_url,
        min_interval=0.0,
    )
