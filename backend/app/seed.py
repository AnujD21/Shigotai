"""Seeds the local database with the demo job dataset and a demo account so
the app is fully explorable without any external integration (master spec
section 48). Safe to re-run: ingestion upserts by source_job_id.

Usage: python -m app.seed
"""

from app.database.session import SessionLocal
from app.ingestion.demo_source import DemoJobSource
from app.ingestion.pipeline import ingest_source
from app.matching.skill_taxonomy import is_ai_ml_skill
from app.models.enums import EmploymentType, JapaneseLevel, JLPTLevel, WorkMode
from app.models.profile import Certification, Education, Profile, UserSkill
from app.models.user import User
from app.services.auth_service import register_user
from app.services.match_service import recompute_matches_for_user
from app.services.profile_service import get_or_create_skill

DEMO_EMAIL = "demo@shigotai.app"
DEMO_PASSWORD = "ShigotaiDemo123!"


def seed_demo_user(db) -> User:
    user = db.query(User).filter(User.email == DEMO_EMAIL).first()
    if user:
        return user

    user = register_user(db, "Aiko Tanaka", DEMO_EMAIL, DEMO_PASSWORD)
    profile: Profile = user.profile
    profile.country = "India"
    profile.current_location = "Bengaluru, India"
    profile.preferred_japan_locations = ["Tokyo", "Yokohama", "Osaka"]
    profile.years_of_experience = 2.5
    profile.is_new_graduate = False
    profile.jlpt_level = JLPTLevel.N3
    profile.japanese_speaking_level = JapaneseLevel.CONVERSATIONAL
    profile.japanese_reading_level = JapaneseLevel.CONVERSATIONAL
    profile.japanese_writing_level = JapaneseLevel.BASIC
    profile.business_japanese_ability = JapaneseLevel.CONVERSATIONAL
    profile.english_level = JapaneseLevel.FLUENT
    profile.desired_roles = ["AI Engineer", "Computer Vision Engineer", "Machine Learning Engineer"]
    profile.work_mode_preference = WorkMode.HYBRID
    profile.employment_type_preference = EmploymentType.FULL_TIME
    profile.visa_sponsorship_required = True

    profile.education.append(
        Education(degree="Bachelor's degree", university="National Institute of Technology", field_of_study="Computer Science", graduation_year=2023)
    )
    profile.certifications.append(Certification(name="JLPT N3", issuer="Japan Foundation", year=2023))

    for skill_name in ["Python", "PyTorch", "OpenCV", "YOLO", "Docker", "React", "SQL", "scikit-learn", "AWS"]:
        skill = get_or_create_skill(db, skill_name)
        profile.skills.append(UserSkill(profile_id=profile.id, skill_id=skill.id, is_ai_ml=is_ai_ml_skill(skill_name)))

    db.commit()
    return user


def main():
    db = SessionLocal()
    try:
        print("Ingesting demo jobs...")
        jobs = ingest_source(db, DemoJobSource(), is_demo=True)
        print(f"Ingested {len(jobs)} demo jobs.")

        print("Seeding demo user...")
        user = seed_demo_user(db)
        print(f"Demo login: {DEMO_EMAIL} / {DEMO_PASSWORD}")

        print("Computing matches for demo user...")
        matches = recompute_matches_for_user(db, user, notify=True)
        print(f"Computed {len(matches)} matches.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
