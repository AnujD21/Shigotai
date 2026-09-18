from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.database.session import get_db
from app.models.enums import JobStatus
from app.models.job import Job, JobRequirement, JobSource, JobVerification
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


class SourceStatus(BaseModel):
    id: str
    name: str
    source_type: str
    is_active: bool
    last_polled_at: datetime | None
    job_count: int


class SystemHealth(BaseModel):
    environment: str
    demo_mode: bool
    llm_provider: str
    email_provider: str
    total_jobs: int
    active_jobs: int
    stale_jobs: int
    unknown_jobs: int
    extraction_coverage_percent: int
    last_verification_at: datetime | None


@router.get("/system-health", response_model=SystemHealth)
def system_health(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    settings = get_settings()
    total = db.query(Job).count()
    active = db.query(Job).filter(Job.status == JobStatus.ACTIVE).count()
    stale = db.query(Job).filter(Job.status == JobStatus.STALE).count()
    unknown = db.query(Job).filter(Job.status == JobStatus.UNKNOWN).count()
    extracted = db.query(JobRequirement).count()
    last_verification = db.query(func.max(JobVerification.checked_at)).scalar()

    return SystemHealth(
        environment=settings.environment,
        demo_mode=settings.demo_mode,
        llm_provider=settings.llm_provider,
        email_provider=settings.email_provider,
        total_jobs=total,
        active_jobs=active,
        stale_jobs=stale,
        unknown_jobs=unknown,
        extraction_coverage_percent=round(100 * extracted / total) if total else 0,
        last_verification_at=last_verification,
    )


@router.get("/job-sources", response_model=list[SourceStatus])
def job_sources(_: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sources = db.query(JobSource).all()
    return [
        SourceStatus(
            id=s.id,
            name=s.name,
            source_type=s.source_type,
            is_active=s.is_active,
            last_polled_at=s.last_polled_at,
            job_count=db.query(Job).filter(Job.source_id == s.id).count(),
        )
        for s in sources
    ]
