"""Matching engine orchestrator: Stage 1 (deterministic) -> Stage 2 (semantic)
-> Stage 3 (AI explanation), as specified in master spec section 12.

Deliberately hybrid: the expensive LLM explanation only runs for jobs that
already cleared the cheap deterministic + embedding stages, which is the
cost-control architecture from section 41.
"""

from sqlalchemy.orm import Session

from app.ai.provider import get_llm_provider
from app.matching.deterministic import evaluate
from app.matching.embeddings import content_hash, cosine_similarity, vectorize_skills, vectorize_text
from app.models.enums import MatchStrength
from app.models.interaction import Match
from app.models.job import Job, JobEmbedding
from app.models.profile import Profile

EXPLANATION_SCORE_THRESHOLD = 0.35


def _get_or_build_job_embedding(db: Session, job: Job) -> JobEmbedding:
    text = f"{job.title}\n{job.original_description}"
    text_hash = content_hash(text)
    if job.embedding and job.embedding.source_text_hash == text_hash:
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


def _strength(overall_score: float, hard_blockers_missing: int) -> MatchStrength:
    if hard_blockers_missing == 0 and overall_score >= 0.72:
        return MatchStrength.STRONG
    if overall_score >= 0.42:
        return MatchStrength.PARTIAL
    return MatchStrength.SIGNIFICANT_GAPS


def compute_match(db: Session, profile: Profile, job: Job, generate_explanation: bool = True) -> Match:
    requirement = job.requirement
    det = evaluate(profile, requirement, job.location, job.work_mode.value) if requirement else None

    job_embedding = _get_or_build_job_embedding(db, job)
    user_vector = vectorize_skills([us.skill.name for us in profile.skills if us.skill])
    semantic_score = cosine_similarity(job_embedding.vector, user_vector)

    required_ratio = det.required_skill_ratio if det else 0.5
    preferred_ratio = det.preferred_skill_ratio if det else 0.5
    hard_blockers = det.hard_blockers_missing if det else 0

    overall_score = max(
        0.0,
        min(
            1.0,
            0.5 * required_ratio + 0.2 * preferred_ratio + 0.3 * semantic_score - 0.15 * hard_blockers,
        ),
    )
    strength = _strength(overall_score, hard_blockers)
    breakdown = [
        {"label": r.label, "category": r.category, "state": r.state, "detail": r.detail} for r in (det.rows if det else [])
    ]

    explanation = None
    if generate_explanation and overall_score >= EXPLANATION_SCORE_THRESHOLD:
        provider = get_llm_provider()
        explanation = provider.explain_match(job.title, job.company.name, breakdown, strength.value)

    existing = db.query(Match).filter(Match.user_id == profile.user_id, Match.job_id == job.id).first()
    if existing is None:
        existing = Match(user_id=profile.user_id, job_id=job.id)
        db.add(existing)

    existing.deterministic_pass = hard_blockers == 0
    existing.semantic_score = semantic_score
    existing.overall_score = overall_score
    existing.match_strength = strength
    existing.requirement_breakdown = breakdown
    existing.ai_explanation = explanation

    db.flush()
    return existing
