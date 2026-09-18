from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.enums import MatchStrength
from app.models.interaction import Match
from app.models.job import Job
from app.models.user import User
from app.schemas.match import MatchListResponse, MatchOut
from app.services.match_service import recompute_matches_for_user

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("", response_model=MatchListResponse)
def get_matches(
    min_strength: MatchStrength | None = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Match)
        .options(joinedload(Match.job).joinedload(Job.company), joinedload(Match.job).joinedload(Job.requirement))
        .filter(Match.user_id == current_user.id)
    )
    if min_strength:
        order = [MatchStrength.SIGNIFICANT_GAPS, MatchStrength.PARTIAL, MatchStrength.STRONG]
        allowed = order[order.index(min_strength):]
        query = query.filter(Match.match_strength.in_(allowed))

    matches = query.order_by(Match.overall_score.desc()).limit(min(100, limit)).all()
    for m in matches:
        m.job.match_score = m.overall_score
        m.job.match_strength = m.match_strength.value
    return MatchListResponse(items=matches, total=len(matches))


@router.get("/by-job/{job_id}", response_model=MatchOut)
def get_match_by_job(job_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    match = (
        db.query(Match)
        .options(joinedload(Match.job).joinedload(Job.company), joinedload(Match.job).joinedload(Job.requirement))
        .filter(Match.job_id == job_id, Match.user_id == current_user.id)
        .first()
    )
    if not match:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No match computed yet for this job.")
    match.job.match_score = match.overall_score
    match.job.match_strength = match.match_strength.value
    return match


@router.get("/{match_id}", response_model=MatchOut)
def get_match(match_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    match = (
        db.query(Match)
        .options(joinedload(Match.job).joinedload(Job.company), joinedload(Match.job).joinedload(Job.requirement))
        .filter(Match.id == match_id, Match.user_id == current_user.id)
        .first()
    )
    if not match:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Match not found.")
    match.job.match_score = match.overall_score
    match.job.match_strength = match.match_strength.value
    return match


@router.post("/recompute", response_model=MatchListResponse)
def recompute(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    matches = recompute_matches_for_user(db, current_user)
    for m in matches:
        m.job.match_score = m.overall_score
        m.job.match_strength = m.match_strength.value
    matches.sort(key=lambda m: m.overall_score, reverse=True)
    return MatchListResponse(items=matches, total=len(matches))
