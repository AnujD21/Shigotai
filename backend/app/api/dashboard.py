from collections import Counter
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.enums import MatchStrength
from app.models.interaction import Application, Match, SavedJob
from app.models.job import Job
from app.models.notification import Notification
from app.models.profile import Profile
from app.models.user import User
from app.schemas.job import JobCard
from app.schemas.notification import NotificationOut
from app.services.profile_service import compute_completeness

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class SkillGapItem(BaseModel):
    skill: str
    missing_count: int


class JapaneseDistributionItem(BaseModel):
    level: str
    job_count: int


class DashboardSummary(BaseModel):
    profile_completeness: int
    completeness_suggestions: list[str]
    new_jobs_today: int
    highly_relevant_count: int
    saved_jobs_count: int
    applications_count: int
    companies_hiring_count: int
    top_matches: list[JobCard]
    skill_gaps: list[SkillGapItem]
    japanese_requirement_distribution: list[JapaneseDistributionItem]
    recent_alerts: list[NotificationOut]


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    completeness, suggestions = compute_completeness(profile) if profile else (0, [])

    since_today = datetime.now(timezone.utc) - timedelta(hours=24)
    new_jobs_today = db.query(Job).filter(Job.first_seen_at >= since_today).count()

    matches = (
        db.query(Match)
        .options(joinedload(Match.job).joinedload(Job.company), joinedload(Match.job).joinedload(Job.requirement))
        .filter(Match.user_id == current_user.id)
        .order_by(Match.overall_score.desc())
        .all()
    )
    highly_relevant = sum(1 for m in matches if m.match_strength == MatchStrength.STRONG)
    top = matches[:5]
    for m in top:
        m.job.match_score = m.overall_score
        m.job.match_strength = m.match_strength.value

    saved_count = db.query(SavedJob).filter(SavedJob.user_id == current_user.id, SavedJob.archived.is_(False)).count()
    applications_count = db.query(Application).filter(Application.user_id == current_user.id).count()
    companies_hiring = db.query(Job.company_id).distinct().count()

    gap_counter: Counter[str] = Counter()
    for m in matches[:20]:
        for row in m.requirement_breakdown:
            if row["category"] in ("required_skill", "preferred_skill") and row["state"] == "MISSING":
                gap_counter[row["label"]] += 1
    skill_gaps = [SkillGapItem(skill=skill, missing_count=count) for skill, count in gap_counter.most_common(6)]

    jlpt_counter: Counter[str] = Counter()
    for job in db.query(Job).options(joinedload(Job.requirement)).all():
        if job.requirement and job.requirement.jlpt_requirement:
            jlpt_counter[job.requirement.jlpt_requirement.value] += 1
        elif job.requirement and job.requirement.japanese_requirement_raw:
            jlpt_counter["Business Japanese (no JLPT specified)"] += 1
    japanese_distribution = [JapaneseDistributionItem(level=level, job_count=count) for level, count in jlpt_counter.most_common()]

    alerts = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.sent_at.desc())
        .limit(5)
        .all()
    )

    return DashboardSummary(
        profile_completeness=completeness,
        completeness_suggestions=suggestions,
        new_jobs_today=new_jobs_today,
        highly_relevant_count=highly_relevant,
        saved_jobs_count=saved_count,
        applications_count=applications_count,
        companies_hiring_count=companies_hiring,
        top_matches=[m.job for m in top],
        skill_gaps=skill_gaps,
        japanese_requirement_distribution=japanese_distribution,
        recent_alerts=alerts,
    )
