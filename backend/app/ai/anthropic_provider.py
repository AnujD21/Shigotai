"""Anthropic-backed extraction provider.

Used when LLM_PROVIDER=anthropic and LLM_API_KEY is set. Structured outputs
constrain the response to the same Pydantic contracts the other providers
use, and any API error, refusal, or truncated response falls back to the
rule-based DevLLMProvider so the pipeline never hard-fails.
"""

import json
import logging
from typing import TypeVar

import anthropic
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

# Extraction and short explanations don't benefit from deep reasoning; low
# effort keeps latency inside a web request and cost near zero.
_EFFORT = "low"


class AnthropicLLMProvider(LLMProvider):
    is_llm = True

    def __init__(self, api_key: str, model: str):
        self._client = anthropic.Anthropic(api_key=api_key, timeout=60.0, max_retries=2)
        self._model = model
        self._fallback = DevLLMProvider()

    def _parse(self, system: str, user: str, output_type: type[T], max_tokens: int) -> T | None:
        try:
            response = self._client.messages.parse(
                model=self._model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
                output_format=output_type,
                output_config={"effort": _EFFORT},
            )
        except anthropic.NotFoundError:
            logger.error("Anthropic model %r not found -- check LLM_MODEL", self._model)
            return None
        except anthropic.RateLimitError:
            logger.warning("Anthropic rate limit hit; using rule-based fallback for this call")
            return None
        except anthropic.APIStatusError as exc:
            logger.warning("Anthropic API error %s: %s", exc.status_code, exc.message)
            return None
        except anthropic.APIConnectionError:
            logger.warning("Couldn't reach the Anthropic API; using rule-based fallback")
            return None
        except pydantic.ValidationError:
            logger.warning("Anthropic response didn't match %s", output_type.__name__)
            return None

        if response.stop_reason != "end_turn":
            # "refusal" or "max_tokens": either way the JSON can't be trusted.
            logger.warning("Anthropic extraction stopped with %s", response.stop_reason)
            return None
        return response.parsed_output

    def extract_requirements(self, job_title: str, description: str, language: str) -> ExtractionJSON:
        parsed = self._parse(
            JOB_EXTRACTION_SYSTEM_PROMPT,
            f"<job_title>{job_title}</job_title>\n<job_posting>\n{description}\n</job_posting>",
            JobRequirementsLLM,
            max_tokens=4000,
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
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=2000,
                system=MATCH_EXPLANATION_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": f"Job: {job_title} at {company_name}\nMatch strength: {match_strength}\n"
                        f"Requirement breakdown: {json.dumps(requirement_breakdown, ensure_ascii=False)}",
                    }
                ],
                output_config={"effort": _EFFORT},
            )
        except anthropic.APIError:
            logger.warning("Anthropic explanation failed; using rule-based explanation")
            return self._fallback.explain_match(job_title, company_name, requirement_breakdown, match_strength)

        # Current models may return thinking blocks before the answer, so pick
        # the text block rather than assuming it's content[0].
        text = next((block.text for block in response.content if block.type == "text"), "").strip()
        if response.stop_reason != "end_turn" or not text:
            return self._fallback.explain_match(job_title, company_name, requirement_breakdown, match_strength)
        return text

    def extract_resume(self, resume_text: str) -> ResumeLLMExtraction | None:
        return self._parse(
            RESUME_EXTRACTION_SYSTEM_PROMPT,
            f"<resume>\n{resume_text}\n</resume>",
            ResumeLLMExtraction,
            max_tokens=8000,
        )
