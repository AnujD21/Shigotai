from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_current_user_optional
from app.database.session import get_db
from app.models.enums import EmploymentType, WorkMode
from app.models.interaction import SavedJob
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobDetail, JobListResponse
from app.services.job_service import JobFilters, list_jobs

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=JobListResponse)
def get_jobs(
    q: str | None = None,
    location: str | None = None,
    company_id: str | None = None,
    employment_type: EmploymentType | None = None,
    work_mode: WorkMode | None = None,
    only_verified_active: bool = False,
    new_graduate: bool | None = None,
    visa_sponsorship: bool | None = None,
    skill: str | None = None,
    sort: str = "recently_verified",
    page: int = 1,
    page_size: int = 20,
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    filters = JobFilters(
        search=q,
        location=location,
        company_id=company_id,
        employment_type=employment_type,
        work_mode=work_mode,
        only_verified_active=only_verified_active,
        new_graduate=new_graduate,
        visa_sponsorship=visa_sponsorship,
        skill=skill,
        sort=sort,
        page=max(1, page),
        page_size=min(50, max(1, page_size)),
    )
    items, total = list_jobs(db, filters, user_id=current_user.id if current_user else None)
    return JobListResponse(items=items, total=total, page=filters.page, page_size=filters.page_size)


@router.get("/{job_id}", response_model=JobDetail)
def get_job(job_id: str, current_user: User | None = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    job = (
        db.query(Job)
        .options(joinedload(Job.company), joinedload(Job.requirement))
        .filter(Job.id == job_id)
        .first()
    )
    if not job:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found.")

    job.match_score = None
    job.match_strength = None
    if current_user:
        from app.models.interaction import Match

        match = db.query(Match).filter(Match.user_id == current_user.id, Match.job_id == job.id).first()
        if match:
            job.match_score = match.overall_score
            job.match_strength = match.match_strength.value
    return job


@router.post("/{job_id}/save", status_code=status.HTTP_204_NO_CONTENT)
def save_job(job_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found.")
    existing = db.query(SavedJob).filter(SavedJob.user_id == current_user.id, SavedJob.job_id == job_id).first()
    if existing:
        existing.archived = False
        db.commit()
        return None
    db.add(SavedJob(user_id=current_user.id, job_id=job_id))
    db.commit()
    return None


@router.delete("/{job_id}/save", status_code=status.HTTP_204_NO_CONTENT)
def unsave_job(job_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(SavedJob).filter(SavedJob.user_id == current_user.id, SavedJob.job_id == job_id).delete()
    db.commit()
    return None
