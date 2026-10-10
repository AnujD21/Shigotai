from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ai.provider import get_llm_provider
from app.matching.skill_taxonomy import canonical_skill_name
from app.models.enums import JapaneseLevel, JLPTLevel, VisaSponsorship
from app.models.job import Job, JobRequirement

_VALID_JLPT = {level.value for level in JLPTLevel}
_VALID_VISA = {v.value for v in VisaSponsorship}
_MAX_LLM_DESCRIPTION_CHARS = 12_000


def _to_jlpt(value: str | None) -> JLPTLevel | None:
    if value and value.upper() in _VALID_JLPT:
        return JLPTLevel(value.upper())
    return None


def _to_visa(value: str) -> VisaSponsorship:
    return VisaSponsorship(value) if value in _VALID_VISA else VisaSponsorship.NOT_STATED


def _dedupe_skills(skills: list[str]) -> list[str]:
    """Canonical names ("pytorch" -> "PyTorch"), first occurrence wins."""
    seen: dict[str, str] = {}
    for skill in skills:
        name = canonical_skill_name(skill)
        if name and name.lower() not in seen:
            seen[name.lower()] = name
    return list(seen.values())


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
    description = job.original_description
    if provider.is_llm and len(description) > _MAX_LLM_DESCRIPTION_CHARS:
        # Requirements sit near the top of a posting; the tail is usually
        # benefits and equal-opportunity boilerplate. Capping keeps a full
        # ingestion run inside free-tier token budgets.
        description = description[:_MAX_LLM_DESCRIPTION_CHARS]
    result = provider.extract_requirements(job.title, description, job.description_language)

    if existing is None:
        existing = JobRequirement()
        job.requirement = existing
        db.add(existing)

    required = _dedupe_skills(result["required_skills"])
    existing.required_skills = required
    existing.preferred_skills = [s for s in _dedupe_skills(result["preferred_skills"]) if s not in required]
    existing.minimum_experience_years = result["minimum_experience"]
    existing.education_requirement = result["education_requirement"]
    existing.jlpt_requirement = _to_jlpt(result["jlpt_requirement"])
    existing.japanese_requirement_raw = result["japanese_requirement"]
    existing.japanese_requirement_level = _infer_language_level(result["japanese_requirement"])
    existing.english_requirement_raw = result["english_requirement"]
    existing.english_requirement_level = _infer_language_level(result["english_requirement"])
    existing.visa_sponsorship = _to_visa(result["visa_sponsorship"])
    existing.new_graduate_allowed = result["new_graduate_allowed"]
    existing.extraction_source = "LLM" if provider.is_llm else "RULE_BASED"
    existing.extraction_confidence = 0.85 if existing.extraction_source == "LLM" else 0.6
    existing.extracted_at = datetime.now(timezone.utc)
    existing.raw_extraction_json = {**result, "content_hash": job.content_hash}

    db.flush()
    return existing
