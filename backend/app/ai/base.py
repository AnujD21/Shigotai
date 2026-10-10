from abc import ABC, abstractmethod
from typing import TypedDict

from app.ai.schemas import ResumeLLMExtraction


class ExtractionJSON(TypedDict):
    required_skills: list[str]
    preferred_skills: list[str]
    minimum_experience: float | None
    education_requirement: str | None
    jlpt_requirement: str | None
    japanese_requirement: str | None
    english_requirement: str | None
    new_graduate_allowed: bool | None
    visa_sponsorship: str


class LLMProvider(ABC):
    """Structured requirement extraction and match explanation.

    Every implementation MUST return `None`/`NOT_STATED` for any field the
    source text does not clearly support. Inventing a requirement that is not
    present in the source text is a product-correctness bug, not a style
    choice -- see master spec section 50 (FACT vs AI INTERPRETATION vs UNKNOWN).
    """

    # True for providers that call a real model; used to label extraction
    # provenance (LLM vs RULE_BASED) on stored requirements.
    is_llm: bool = False

    @abstractmethod
    def extract_requirements(self, job_title: str, description: str, language: str) -> ExtractionJSON: ...

    @abstractmethod
    def explain_match(
        self,
        job_title: str,
        company_name: str,
        requirement_breakdown: list[dict],
        match_strength: str,
    ) -> str: ...

    def extract_resume(self, resume_text: str) -> ResumeLLMExtraction | None:
        """Structured resume fields, or None when this provider can't (the
        caller then falls back to heuristic parsing)."""
        return None
