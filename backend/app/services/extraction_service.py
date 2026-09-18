from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ai.provider import get_llm_provider
from app.models.enums import JapaneseLevel, JLPTLevel, VisaSponsorship
from app.models.job import Job, JobRequirement

_VALID_JLPT = {level.value for level in JLPTLevel}
_VALID_VISA = {v.value for v in VisaSponsorship}


def _to_jlpt(value: str | None) -> JLPTLevel | None:
    if value and value.upper() in _VALID_JLPT:
        return JLPTLevel(value.upper())
    return None


def _to_visa(value: str) -> VisaSponsorship:
    return VisaSponsorship(value) if value in _VALID_VISA else VisaSponsorship.NOT_STATED


def _infer_language_level(raw: str | None) -> JapaneseLevel | None:
    if not raw:
        return None
    lowered = raw.lower()
    if "business" in lowered:
        return JapaneseLevel.BUSINESS
    if "fluent" in lowered:
        return JapaneseLevel.FLUENT
    if "native" in lowered:
        return JapaneseLevel.NATIVE
    if "conversational" in lowered:
        return JapaneseLevel.CONVERSATIONAL
    return None


def extract_job_requirements(db: Session, job: Job, force: bool = False) -> JobRequirement:
    """Run (or reuse cached) structured requirement extraction for a job.

    Caching by content_hash avoids re-processing an unchanged job description
    through the LLM on every ingestion cycle (master spec section 41).
    """
    existing = job.requirement
    if existing and not force and existing.raw_extraction_json.get("content_hash") == job.content_hash:
        return existing

    provider = get_llm_provider()
    result = provider.extract_requirements(job.title, job.original_description, job.description_language)

    if existing is None:
        existing = JobRequirement()
        job.requirement = existing
        db.add(existing)

    existing.required_skills = result["required_skills"]
    existing.preferred_skills = result["preferred_skills"]
    existing.minimum_experience_years = result["minimum_experience"]
    existing.education_requirement = result["education_requirement"]
    existing.jlpt_requirement = _to_jlpt(result["jlpt_requirement"])
    existing.japanese_requirement_raw = result["japanese_requirement"]
    existing.japanese_requirement_level = _infer_language_level(result["japanese_requirement"])
    existing.english_requirement_raw = result["english_requirement"]
    existing.english_requirement_level = _infer_language_level(result["english_requirement"])
    existing.visa_sponsorship = _to_visa(result["visa_sponsorship"])
    existing.new_graduate_allowed = result["new_graduate_allowed"]
    existing.extraction_source = "LLM" if provider.__class__.__name__ == "AnthropicLLMProvider" else "RULE_BASED"
    existing.extraction_confidence = 0.85 if existing.extraction_source == "LLM" else 0.6
    existing.extracted_at = datetime.now(timezone.utc)
    existing.raw_extraction_json = {**result, "content_hash": job.content_hash}

    db.flush()
    return existing
