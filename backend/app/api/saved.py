from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.enums import ApplicationStatus
from app.models.interaction import Application, SavedJob
from app.models.job import Job
from app.models.user import User
from app.schemas.company import ApplicationOut, SavedJobOut

router = APIRouter(tags=["saved"])


@router.get("/saved-jobs", response_model=list[SavedJobOut])
def list_saved_jobs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    saved = (
        db.query(SavedJob)
        .options(joinedload(SavedJob.job).joinedload(Job.company), joinedload(SavedJob.job).joinedload(Job.requirement))
        .filter(SavedJob.user_id == current_user.id, SavedJob.archived.is_(False))
        .order_by(SavedJob.saved_at.desc())
        .all()
    )
    applications = {
        a.job_id: a.status.value
        for a in db.query(Application).filter(Application.user_id == current_user.id).all()
    }
    results = []
    for s in saved:
        s.job.match_score = None
        s.job.match_strength = None
        results.append(
            SavedJobOut(
                id=s.id,
                job=s.job,
                saved_at=s.saved_at.isoformat(),
                application_status=applications.get(s.job_id),
            )
        )
    return results


class ApplicationUpdate(BaseModel):
    status: ApplicationStatus
    notes: str | None = None


@router.get("/applications", response_model=list[ApplicationOut])
def list_applications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    applications = (
        db.query(Application)
        .options(joinedload(Application.job).joinedload(Job.company), joinedload(Application.job).joinedload(Job.requirement))
        .filter(Application.user_id == current_user.id)
        .order_by(Application.status_updated_at.desc())
        .all()
    )
    results = []
    for a in applications:
        if a.job is None:
            # Defensive: a row whose job was deleted/invalid shouldn't 500 the
            # whole list. Shouldn't happen going forward now that PUT
            # /applications/{job_id} validates job_id, but guards against
            # any pre-existing orphaned rows.
            continue
        a.job.match_score = None
        a.job.match_strength = None
        results.append(
            ApplicationOut(
                id=a.id,
                job=a.job,
                status=a.status.value,
                applied_at=a.applied_at.isoformat() if a.applied_at else None,
                status_updated_at=a.status_updated_at.isoformat(),
                notes=a.notes,
            )
        )
    return results


@router.put("/applications/{job_id}", response_model=ApplicationOut)
def upsert_application(job_id: str, payload: ApplicationUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    job = db.query(Job).options(joinedload(Job.company), joinedload(Job.requirement)).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found.")

    application = db.query(Application).filter(Application.user_id == current_user.id, Application.job_id == job_id).first()
    now = datetime.now(timezone.utc)
    if application is None:
        application = Application(user_id=current_user.id, job_id=job_id, status=payload.status, notes=payload.notes)
        if payload.status != ApplicationStatus.SAVED:
            application.applied_at = now
        db.add(application)
    else:
        application.status = payload.status
        application.notes = payload.notes
        application.status_updated_at = now
        if payload.status == ApplicationStatus.APPLIED and application.applied_at is None:
            application.applied_at = now
    db.commit()
    db.refresh(application)
    db.refresh(job)

    job.match_score = None
    job.match_strength = None
    return ApplicationOut(
        id=application.id,
        job=job,
        status=application.status.value,
        applied_at=application.applied_at.isoformat() if application.applied_at else None,
        status_updated_at=application.status_updated_at.isoformat(),
        notes=application.notes,
    )
