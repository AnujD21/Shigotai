from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.profile import (
    CertificationIn,
    EducationIn,
    ExperienceIn,
    ProfileOut,
    ProfileUpdate,
    ProjectIn,
    SkillIn,
)
from app.services.profile_service import compute_completeness, get_or_create_profile, update_profile

router = APIRouter(prefix="/profile", tags=["profile"])


def _serialize(profile) -> ProfileOut:
    completeness, suggestions = compute_completeness(profile)
    return ProfileOut(
        id=profile.id,
        user_id=profile.user_id,
        country=profile.country,
        current_location=profile.current_location,
        preferred_japan_locations=profile.preferred_japan_locations,
        years_of_experience=profile.years_of_experience,
        is_new_graduate=profile.is_new_graduate,
        jlpt_level=profile.jlpt_level,
        japanese_speaking_level=profile.japanese_speaking_level,
        japanese_reading_level=profile.japanese_reading_level,
        japanese_writing_level=profile.japanese_writing_level,
        business_japanese_ability=profile.business_japanese_ability,
        english_level=profile.english_level,
        desired_roles=profile.desired_roles,
        work_mode_preference=profile.work_mode_preference,
        employment_type_preference=profile.employment_type_preference,
        salary_expectation_min=profile.salary_expectation_min,
        salary_expectation_max=profile.salary_expectation_max,
        company_size_preference=profile.company_size_preference,
        industry_preference=profile.industry_preference,
        visa_sponsorship_required=profile.visa_sponsorship_required,
        resume_original_filename=profile.resume_original_filename,
        education=[EducationIn.model_validate(e, from_attributes=True) for e in profile.education],
        experience=[ExperienceIn.model_validate(e, from_attributes=True) for e in profile.experience],
        projects=[ProjectIn.model_validate(p, from_attributes=True) for p in profile.projects],
        certifications=[CertificationIn.model_validate(c, from_attributes=True) for c in profile.certifications],
        skills=[
            SkillIn(name=s.skill.name, proficiency=s.proficiency, years_experience=s.years_experience, is_ai_ml=s.is_ai_ml)
            for s in profile.skills
        ],
        completeness_percent=completeness,
        completeness_suggestions=suggestions,
    )


@router.get("", response_model=ProfileOut)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = get_or_create_profile(db, current_user.id)
    return _serialize(profile)


@router.put("", response_model=ProfileOut)
def put_profile(payload: ProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = get_or_create_profile(db, current_user.id)
    profile = update_profile(db, profile, payload)
    return _serialize(profile)
