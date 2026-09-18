from sqlalchemy.orm import Session

from app.matching.skill_taxonomy import canonical_skill_name, infer_category, is_ai_ml_skill
from app.models.profile import Certification, Education, Experience, Profile, Project, Skill, UserSkill
from app.schemas.profile import ProfileUpdate

_COMPLETENESS_WEIGHTS = [
    ("country", 5),
    ("current_location", 5),
    ("desired_roles", 10),
    ("jlpt_level_or_japanese", 10),
    ("education", 20),
    ("experience_or_new_grad", 10),
    ("skills", 25),
    ("projects", 15),
]


def get_or_create_profile(db: Session, user_id: str) -> Profile:
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if profile is None:
        profile = Profile(user_id=user_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def get_or_create_skill(db: Session, name: str) -> Skill:
    canonical = canonical_skill_name(name)
    skill = db.query(Skill).filter(Skill.name == canonical).first()
    if skill is None:
        skill = Skill(name=canonical, category=infer_category(canonical))
        db.add(skill)
        db.flush()
    return skill


def update_profile(db: Session, profile: Profile, data: ProfileUpdate) -> Profile:
    scalar_fields = data.model_dump(
        exclude_unset=True,
        exclude={"education", "experience", "projects", "certifications", "skills"},
    )
    for field, value in scalar_fields.items():
        setattr(profile, field, value)

    if data.education is not None:
        profile.education.clear()
        db.flush()
        for item in data.education:
            profile.education.append(Education(**item.model_dump(exclude={"id"})))

    if data.experience is not None:
        profile.experience.clear()
        db.flush()
        for item in data.experience:
            profile.experience.append(Experience(**item.model_dump(exclude={"id"})))

    if data.projects is not None:
        profile.projects.clear()
        db.flush()
        for item in data.projects:
            profile.projects.append(Project(**item.model_dump(exclude={"id"})))

    if data.certifications is not None:
        profile.certifications.clear()
        db.flush()
        for item in data.certifications:
            profile.certifications.append(Certification(**item.model_dump(exclude={"id"})))

    if data.skills is not None:
        profile.skills.clear()
        db.flush()
        for item in data.skills:
            skill = get_or_create_skill(db, item.name)
            profile.skills.append(
                UserSkill(
                    profile_id=profile.id,
                    skill_id=skill.id,
                    proficiency=item.proficiency,
                    years_experience=item.years_experience,
                    is_ai_ml=item.is_ai_ml or is_ai_ml_skill(item.name),
                )
            )

    db.commit()
    db.refresh(profile)
    return profile


def compute_completeness(profile: Profile) -> tuple[int, list[str]]:
    earned = 0
    total = sum(weight for _, weight in _COMPLETENESS_WEIGHTS)
    suggestions: list[str] = []

    if profile.country:
        earned += 5
    else:
        suggestions.append("Add your current country.")

    if profile.current_location:
        earned += 5
    else:
        suggestions.append("Add your current location.")

    if profile.desired_roles:
        earned += 10
    else:
        suggestions.append("Add at least one desired job role.")

    if profile.jlpt_level.value != "NONE" or profile.business_japanese_ability.value != "NONE":
        earned += 10
    else:
        suggestions.append("Add your Japanese ability, even if it's just getting started.")

    if profile.education:
        earned += 20
    else:
        suggestions.append("Add your education history.")

    if profile.experience or profile.is_new_graduate:
        earned += 10
    else:
        suggestions.append("Add your work experience, or mark yourself as a new graduate.")

    if len(profile.skills) >= 5:
        earned += 25
    elif profile.skills:
        earned += 12
        suggestions.append(f"Add {5 - len(profile.skills)} more skills to improve matching.")
    else:
        suggestions.append("Add your technical skills.")

    if len(profile.projects) >= 2:
        earned += 15
    elif profile.projects:
        earned += 7
        suggestions.append("Add one more project to strengthen your profile.")
    else:
        suggestions.append("Add 2 projects to improve matching.")

    return round(100 * earned / total), suggestions
