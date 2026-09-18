from sqlalchemy.orm import Session, joinedload

from app.matching.engine import compute_match
from app.models.enums import JobStatus
from app.models.interaction import Match
from app.models.job import Job
from app.models.notification import NotificationPreference
from app.models.profile import Profile
from app.models.user import User
from app.services.notification_service import maybe_notify

FRONTEND_JOB_URL = "http://localhost:3000/jobs/{job_id}"


def recompute_matches_for_user(db: Session, user: User, notify: bool = True) -> list[Match]:
    """Recompute every active job's match for one user.

    This runs synchronously and in-process, which is appropriate at demo
    scale (dozens of jobs). At production scale this becomes a background
    worker step triggered by profile changes and new job ingestion (master
    spec sections 15 & 42) -- the function signature would stay the same.
    """
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if profile is None:
        return []

    preference = db.query(NotificationPreference).filter(NotificationPreference.user_id == user.id).first()
    jobs = (
        db.query(Job)
        .options(joinedload(Job.company), joinedload(Job.requirement))
        .filter(Job.status == JobStatus.ACTIVE)
        .all()
    )

    results = []
    for job in jobs:
        previous = db.query(Match).filter(Match.user_id == user.id, Match.job_id == job.id).first()
        previous_strength = previous.match_strength if previous else None
        previous_pass = previous.deterministic_pass if previous else None

        match = compute_match(db, profile, job)
        results.append(match)

        if notify and preference:
            maybe_notify(
                db,
                match,
                job,
                preference,
                previous_strength,
                previous_pass,
                user.email,
                FRONTEND_JOB_URL.format(job_id=job.id),
            )

    db.commit()
    return results


def recompute_matches_for_job(db: Session, job: Job, notify: bool = True) -> list[Match]:
    """Recompute one job's match across every user (used after ingestion
    picks up a new/changed posting -- master spec section 15's NEW JOB flow).
    """
    preference_by_user = {p.user_id: p for p in db.query(NotificationPreference).all()}
    profiles = db.query(Profile).all()
    users_by_id = {u.id: u for u in db.query(User).all()}

    results = []
    for profile in profiles:
        user = users_by_id.get(profile.user_id)
        if not user:
            continue
        previous = db.query(Match).filter(Match.user_id == user.id, Match.job_id == job.id).first()
        previous_strength = previous.match_strength if previous else None
        previous_pass = previous.deterministic_pass if previous else None

        match = compute_match(db, profile, job)
        results.append(match)

        preference = preference_by_user.get(user.id)
        if notify and preference:
            maybe_notify(
                db,
                match,
                job,
                preference,
                previous_strength,
                previous_pass,
                user.email,
                FRONTEND_JOB_URL.format(job_id=job.id),
            )

    db.commit()
    return results
