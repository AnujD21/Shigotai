"""Anthropic-backed extraction provider.

Used automatically when LLM_PROVIDER=anthropic and LLM_API_KEY is set. Falls
back to the same strict-JSON contract as DevLLMProvider so the rest of the
pipeline (validation, matching) never needs to know which provider produced
the data.
"""

import json

import httpx

from app.ai.base import ExtractionJSON, LLMProvider
from app.ai.dev_provider import DevLLMProvider

_EXTRACTION_SYSTEM_PROMPT = """You extract structured hiring requirements from a job posting.
Return ONLY a JSON object with this exact shape:
{
  "required_skills": string[],
  "preferred_skills": string[],
  "minimum_experience": number | null,
  "education_requirement": string | null,
  "jlpt_requirement": string | null,
  "japanese_requirement": string | null,
  "english_requirement": string | null,
  "new_graduate_allowed": boolean | null,
  "visa_sponsorship": "YES" | "NO" | "NOT_STATED"
}
Rules:
- Only include a value when the posting states it explicitly or very clearly implies it.
- Never invent a JLPT level. If Japanese ability is required but no JLPT level is given, set jlpt_requirement to null and describe the requirement in japanese_requirement instead.
- If visa sponsorship is not mentioned, use "NOT_STATED".
- Respond with JSON only, no commentary."""

_EXPLAIN_SYSTEM_PROMPT = """You write a short, honest explanation (2-4 sentences) of why a candidate does or
does not match a job, given a structured requirement breakdown. Be specific, cite the actual
requirement labels, and never claim a match that the data does not support."""


class AnthropicLLMProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        self._api_key = api_key
        self._model = model
        self._fallback = DevLLMProvider()

    def _call(self, system: str, user: str) -> str | None:
        try:
            response = httpx.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self._api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": self._model,
                    "max_tokens": 1024,
                    "system": system,
                    "messages": [{"role": "user", "content": user}],
                },
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]
        except (httpx.HTTPError, KeyError, IndexError):
            return None

    def extract_requirements(self, job_title: str, description: str, language: str) -> ExtractionJSON:
        text = self._call(_EXTRACTION_SYSTEM_PROMPT, f"Job title: {job_title}\n\nDescription:\n{description}")
        if not text:
            return self._fallback.extract_requirements(job_title, description, language)
        try:
            parsed = json.loads(text)
            return ExtractionJSON(
                required_skills=list(parsed.get("required_skills") or []),
                preferred_skills=list(parsed.get("preferred_skills") or []),
                minimum_experience=parsed.get("minimum_experience"),
                education_requirement=parsed.get("education_requirement"),
                jlpt_requirement=parsed.get("jlpt_requirement"),
                japanese_requirement=parsed.get("japanese_requirement"),
                english_requirement=parsed.get("english_requirement"),
                new_graduate_allowed=parsed.get("new_graduate_allowed"),
                visa_sponsorship=parsed.get("visa_sponsorship") or "NOT_STATED",
            )
        except (json.JSONDecodeError, TypeError):
            return self._fallback.extract_requirements(job_title, description, language)

    def explain_match(
        self,
        job_title: str,
        company_name: str,
        requirement_breakdown: list[dict],
        match_strength: str,
    ) -> str:
        text = self._call(
            _EXPLAIN_SYSTEM_PROMPT,
            f"Job: {job_title} at {company_name}\nMatch strength: {match_strength}\n"
            f"Requirement breakdown: {json.dumps(requirement_breakdown)}",
        )
        return text or self._fallback.explain_match(job_title, company_name, requirement_breakdown, match_strength)
