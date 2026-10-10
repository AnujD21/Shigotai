"""Matching engine orchestrator: Stage 1 (deterministic) -> Stage 2 (semantic)
-> Stage 3 (AI explanation), as specified in master spec section 12.

Deliberately hybrid: the expensive LLM explanation only runs for jobs that
already cleared the cheap deterministic + embedding stages, which is the
cost-control architecture from section 41.
"""

from sqlalchemy.orm import Session

from app.ai.base import LLMProvider
from app.ai.dev_provider import DevLLMProvider
from app.ai.provider import get_llm_provider
from app.matching.deterministic import evaluate
from app.matching.roles import role_relevance
from app.matching.embeddings import VECTOR_SIZE, content_hash, cosine_similarity, vectorize_skills, vectorize_text
from app.models.enums import MatchStrength
from app.models.interaction import Match
from app.models.job import Job, JobEmbedding
from app.models.profile import Profile

EXPLANATION_SCORE_THRESHOLD = 0.35
STRONG_ROLE_FIT = 0.5


def _get_or_build_job_embedding(db: Session, job: Job) -> JobEmbedding:
    text = f"{job.title}\n{job.original_description}"
    text_hash = content_hash(text)
    # A catalog change alters the vector's dimensions, so a stored vector of
    # the wrong length is stale even when the job text hasn't changed.
    if job.embedding and job.embedding.source_text_hash == text_hash and len(job.embedding.vector) == VECTOR_SIZE:
        return job.embedding

    vector = vectorize_text(text)
    if job.embedding:
        job.embedding.vector = vector
        job.embedding.source_text_hash = text_hash
        embedding = job.embedding
    else:
        embedding = JobEmbedding(vector=vector, source_text_hash=text_hash)
        job.embedding = embedding
        db.add(embedding)
    db.flush()
    return embedding


def _strength(overall_score: float, hard_blockers_missing: int, role_fit: float | None = None) -> MatchStrength:
    # A strong match has to be the kind of role the candidate asked for, not
    # just a posting that happens to mention their skills.
    role_ok = role_fit is None or role_fit >= STRONG_ROLE_FIT
    if hard_blockers_missing == 0 and overall_score >= 0.72 and role_ok:
        return MatchStrength.STRONG
    if overall_score >= 0.42:
        return MatchStrength.PARTIAL
    return MatchStrength.SIGNIFICANT_GAPS


def _confident_ratio(ratio: float, listed: int) -> float:
    """Shrink a skill-match ratio toward neutral when the posting lists only
    one or two skills: matching 1 of 1 says less than matching 5 of 5."""
    confidence = min(1.0, listed / 3)
    return 0.5 + (ratio - 0.5) * confidence


def _explain(job: Job, breakdown: list[dict], strength: MatchStrength, provider: LLMProvider) -> str:
    return provider.explain_match(job.title, job.company.name, breakdown, strength.value)


def fill_missing_explanations(matches: list[tuple[Match, Job]], llm_budget: int) -> None:
    """Explain matches that cleared the threshold but have no explanation yet.

    The highest-scoring ones (the matches a user actually reads first) get an
    LLM explanation, up to `llm_budget` calls; the rest get the instant
    rule-based one. This bounds LLM calls per recompute no matter how many
    jobs are active.
    """
    rule_based = DevLLMProvider()
    llm = get_llm_provider()
    pending = [
        (match, job)
        for match, job in matches
        if match.ai_explanation is None and match.overall_score >= EXPLANATION_SCORE_THRESHOLD
    ]
    pending.sort(key=lambda pair: pair[0].overall_score, reverse=True)
    for i, (match, job) in enumerate(pending):
        provider = llm if i < llm_budget else rule_based
        match.ai_explanation = _explain(job, match.requirement_breakdown, match.match_strength, provider)


def compute_match(db: Session, profile: Profile, job: Job, generate_explanation: bool = True) -> Match:
    requirement = job.requirement
    det = evaluate(profile, requirement, job.location, job.work_mode.value) if requirement else None

    job_embedding = _get_or_build_job_embedding(db, job)
    user_vector = vectorize_skills([us.skill.name for us in profile.skills if us.skill])
    semantic_score = cosine_similarity(job_embedding.vector, user_vector)

    required_ratio = (
        _confident_ratio(det.required_skill_ratio, len(requirement.required_skills)) if det else 0.5
    )
    preferred_ratio = det.preferred_skill_ratio if det else 0.5
    hard_blockers = det.hard_blockers_missing if det else 0
    role_fit = role_relevance(job.title, profile.desired_roles or [])

    if role_fit is None:
        raw_score = 0.5 * required_ratio + 0.2 * preferred_ratio + 0.3 * semantic_score
    else:
        raw_score = 0.4 * required_ratio + 0.15 * preferred_ratio + 0.25 * semantic_score + 0.2 * role_fit
    overall_score = max(0.0, min(1.0, raw_score - 0.15 * hard_blockers))
    strength = _strength(overall_score, hard_blockers, role_fit)
    breakdown = [
        {"label": r.label, "category": r.category, "state": r.state, "detail": r.detail} for r in (det.rows if det else [])
    ]

    existing = db.query(Match).filter(Match.user_id == profile.user_id, Match.job_id == job.id).first()
    if existing is None:
        existing = Match(user_id=profile.user_id, job_id=job.id)
        db.add(existing)

    # Re-explaining an unchanged match would spend an LLM call to produce the
    # same text, so keep the stored explanation when nothing it describes moved.
    unchanged = (
        existing.ai_explanation is not None
        and existing.requirement_breakdown == breakdown
        and existing.match_strength == strength
    )

    existing.deterministic_pass = hard_blockers == 0
    existing.semantic_score = semantic_score
    existing.overall_score = overall_score
    existing.match_strength = strength
    existing.requirement_breakdown = breakdown

    if overall_score < EXPLANATION_SCORE_THRESHOLD:
        existing.ai_explanation = None
    elif not unchanged:
        existing.ai_explanation = (
            _explain(job, breakdown, strength, get_llm_provider()) if generate_explanation else None
        )

    db.flush()
    return existing
