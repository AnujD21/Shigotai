"""Provider for any OpenAI-compatible chat-completions API.

This is what makes a $0 deployment possible: Groq, Google Gemini, and
OpenRouter all expose free tiers behind this same protocol, so one class
covers them via LLM_BASE_URL (or the presets in provider.py). Responses are
requested in JSON mode and validated against the same Pydantic contracts as
the Anthropic provider; anything invalid falls back to rule-based output.

Free tiers are rate-limited (often ~30 requests/minute), so calls can be
spaced with LLM_MIN_INTERVAL_SECONDS and a 429 is retried once after the
server's retry-after delay.
"""

import json
import logging
import threading
import time
from typing import TypeVar

import httpx
import pydantic

from app.ai.base import ExtractionJSON, LLMProvider
from app.ai.dev_provider import DevLLMProvider
from app.ai.prompts import (
    JOB_EXTRACTION_SYSTEM_PROMPT,
    MATCH_EXPLANATION_SYSTEM_PROMPT,
    RESUME_EXTRACTION_SYSTEM_PROMPT,
)
from app.ai.schemas import JobRequirementsLLM, ResumeLLMExtraction

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=pydantic.BaseModel)

_MAX_RETRY_AFTER_SECONDS = 30.0


def _schema_instruction(output_type: type[pydantic.BaseModel]) -> str:
    schema = json.dumps(output_type.model_json_schema(), ensure_ascii=False)
    return (
        "\n\nRespond with a single JSON object that conforms to this JSON Schema, and nothing else. "
        f"Include every property; use null where the schema allows it and the information is absent.\n{schema}"
    )


class OpenAICompatibleLLMProvider(LLMProvider):
    is_llm = True

    def __init__(self, base_url: str, api_key: str, model: str, min_interval_seconds: float = 0.0):
        self._url = base_url.rstrip("/") + "/chat/completions"
        self._api_key = api_key
        self._model = model
        self._min_interval = min_interval_seconds
        self._last_call = 0.0
        self._lock = threading.Lock()
        self._fallback = DevLLMProvider()

    def _throttle(self) -> None:
        if self._min_interval <= 0:
            return
        with self._lock:
            wait = self._last_call + self._min_interval - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            self._last_call = time.monotonic()

    def _chat(self, system: str, user: str, json_mode: bool, max_tokens: int) -> str | None:
        body: dict = {
            "model": self._model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": 0,
            "max_tokens": max_tokens,
        }
        if json_mode:
            body["response_format"] = {"type": "json_object"}

        for attempt in range(2):
            self._throttle()
            try:
                response = httpx.post(
                    self._url,
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json=body,
                    timeout=60.0,
                )
            except httpx.HTTPError:
                logger.warning("Couldn't reach LLM endpoint %s", self._url)
                return None

            if response.status_code == 429 and attempt == 0:
                retry_after = response.headers.get("retry-after", "")
                try:
                    delay = float(retry_after)
                except ValueError:
                    delay = 10.0
                if delay > _MAX_RETRY_AFTER_SECONDS:
                    logger.warning("LLM rate limit resets in %ss; using rule-based fallback", delay)
                    return None
                time.sleep(delay)
                continue
            if response.status_code >= 400:
                logger.warning("LLM API error %s: %s", response.status_code, response.text[:300])
                return None

            try:
                choice = response.json()["choices"][0]
            except (ValueError, KeyError, IndexError):
                logger.warning("Unexpected LLM response shape from %s", self._url)
                return None
            if choice.get("finish_reason") not in (None, "stop"):
                logger.warning("LLM response ended with %s", choice.get("finish_reason"))
                return None
            return (choice.get("message") or {}).get("content")
        return None

    def _parse(self, system: str, user: str, output_type: type[T], max_tokens: int) -> T | None:
        text = self._chat(system + _schema_instruction(output_type), user, json_mode=True, max_tokens=max_tokens)
        if not text:
            return None
        try:
            return output_type.model_validate_json(text)
        except pydantic.ValidationError:
            logger.warning("LLM response didn't match %s", output_type.__name__)
            return None

    def extract_requirements(self, job_title: str, description: str, language: str) -> ExtractionJSON:
        parsed = self._parse(
            JOB_EXTRACTION_SYSTEM_PROMPT,
            f"<job_title>{job_title}</job_title>\n<job_posting>\n{description}\n</job_posting>",
            JobRequirementsLLM,
            max_tokens=2000,
        )
        if parsed is None:
            return self._fallback.extract_requirements(job_title, description, language)
        return ExtractionJSON(**parsed.model_dump())

    def explain_match(
        self,
        job_title: str,
        company_name: str,
        requirement_breakdown: list[dict],
        match_strength: str,
    ) -> str:
        text = self._chat(
            MATCH_EXPLANATION_SYSTEM_PROMPT,
            f"Job: {job_title} at {company_name}\nMatch strength: {match_strength}\n"
            f"Requirement breakdown: {json.dumps(requirement_breakdown, ensure_ascii=False)}",
            json_mode=False,
            max_tokens=400,
        )
        if not text or not text.strip():
            return self._fallback.explain_match(job_title, company_name, requirement_breakdown, match_strength)
        return text.strip()

    def extract_resume(self, resume_text: str) -> ResumeLLMExtraction | None:
        return self._parse(
            RESUME_EXTRACTION_SYSTEM_PROMPT,
            f"<resume>\n{resume_text}\n</resume>",
            ResumeLLMExtraction,
            max_tokens=4000,
        )
