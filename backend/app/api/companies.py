from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user_optional
from app.database.session import get_db
from app.models.company import Company
from app.models.job import Job
from app.models.profile import Profile
from app.models.user import User
from app.schemas.company import CompanyDetail, CompanyOut, CompatibilityBand

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyOut])
def list_companies(db: Session = Depends(get_db)):
    return db.query(Company).order_by(Company.name).all()


def _compatibility(profile: Profile | None, company: Company) -> list[CompatibilityBand]:
    if not profile:
        return []
    user_skills = {us.skill.name.lower() for us in profile.skills if us.skill}
    required = set()
    for job in company.jobs:
        if job.requirement:
            required.update(s.lower() for s in job.requirement.required_skills)

    if not required:
        skills_band = CompatibilityBand(label="Technical skills", band="UNKNOWN", detail="Not enough job data yet.")
    else:
        overlap = len(user_skills & required) / len(required)
        if overlap >= 0.6:
            skills_band = CompatibilityBand(label="Technical skills", band="STRONG", detail="Strong overlap with skills these roles ask for.")
        elif overlap >= 0.25:
            skills_band = CompatibilityBand(label="Technical skills", band="GOOD", detail="Partial overlap with skills these roles ask for.")
        else:
            skills_band = CompatibilityBand(label="Technical skills", band="LIMITED", detail="Limited overlap with skills these roles ask for.")

    if profile.jlpt_level.value == "NONE" and profile.business_japanese_ability.value == "NONE":
        japanese_band = CompatibilityBand(label="Japanese", band="UNKNOWN", detail="Add your Japanese ability to see this.")
    else:
        japanese_band = CompatibilityBand(label="Japanese", band="GOOD", detail=f"Your level: {profile.jlpt_level.value}")

    if profile.is_new_graduate:
        exp_band = CompatibilityBand(label="Experience", band="GOOD", detail="Entry-level compatible based on new graduate eligibility across open roles.")
    else:
        exp_band = CompatibilityBand(label="Experience", band="GOOD", detail=f"{profile.years_of_experience:g} years of experience on file.")

    return [skills_band, japanese_band, exp_band]


@router.get("/{slug}", response_model=CompanyDetail)
def get_company(slug: str, current_user: User | None = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    company = (
        db.query(Company)
        .options(joinedload(Company.jobs).joinedload(Job.requirement))
        .filter(Company.slug == slug)
        .first()
    )
    if not company:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found.")

    for job in company.jobs:
        job.match_score = None
        job.match_strength = None

    profile = None
    if current_user:
        profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()

    return CompanyDetail(
        **CompanyOut.model_validate(company, from_attributes=True).model_dump(),
        open_positions=company.jobs,
        compatibility=_compatibility(profile, company) if current_user else None,
    )
