from app.matching.engine import compute_match
from app.models.company import Company
from app.models.enums import EmploymentType, JLPTLevel, NotificationFrequency, WorkMode
from app.models.job import Job, JobRequirement
from app.models.notification import Notification, NotificationPreference
from app.models.profile import Profile, UserSkill
from app.models.user import User
from app.services.notification_service import maybe_notify
from app.services.profile_service import get_or_create_skill


def _setup(db, jlpt_required=None, required_skills=None):
    company = Company(name="Acme", slug="acme")
    db.add(company)
    db.flush()
    job = Job(
        company_id=company.id,
        title="Engineer",
        original_description="desc",
        source_url="https://x/1",
        canonical_url="https://x/1",
        content_hash="h1",
        location="Tokyo",
        employment_type=EmploymentType.FULL_TIME,
        work_mode=WorkMode.HYBRID,
    )
    db.add(job)
    db.flush()
    requirement = JobRequirement(job_id=job.id, jlpt_requirement=jlpt_required, required_skills=required_skills or [])
    db.add(requirement)
    db.flush()
    job.requirement = requirement

    user = User(email="notify@example.com", hashed_password="x", full_name="Notify Test")
    db.add(user)
    db.flush()
    profile = Profile(user_id=user.id)
    db.add(profile)
    db.flush()

    preference = NotificationPreference(user_id=user.id, frequency=NotificationFrequency.INSTANT, min_match_threshold=0.1)
    db.add(preference)
    db.flush()

    return job, profile, user, preference


def test_first_match_creates_new_match_notification(db_session):
    job, profile, user, preference = _setup(db_session, required_skills=["Python"])
    skill = get_or_create_skill(db_session, "Python")
    profile.skills.append(UserSkill(profile_id=profile.id, skill_id=skill.id))
    db_session.flush()

    match = compute_match(db_session, profile, job, generate_explanation=False)
    notification = maybe_notify(db_session, match, job, preference, None, None, user.email, "https://app/jobs/1")

    assert notification is not None
    assert notification.type.value == "NEW_MATCH"


def test_recomputing_unchanged_match_does_not_renotify(db_session):
    job, profile, user, preference = _setup(db_session, required_skills=["Python"])
    skill = get_or_create_skill(db_session, "Python")
    profile.skills.append(UserSkill(profile_id=profile.id, skill_id=skill.id))
    db_session.flush()

    match = compute_match(db_session, profile, job, generate_explanation=False)
    first = maybe_notify(db_session, match, job, preference, None, None, user.email, "https://app/jobs/1")
    assert first is not None

    # Recompute again with the same inputs -- this simulates a routine
    # re-scan that found nothing new (master spec section 18).
    match2 = compute_match(db_session, profile, job, generate_explanation=False)
    second = maybe_notify(
        db_session, match2, job, preference, match.match_strength, match.deterministic_pass, user.email, "https://app/jobs/1"
    )
    assert second is None
    assert db_session.query(Notification).count() == 1


def test_job_update_that_newly_clears_requirement_triggers_became_match(db_session):
    """Master spec section 19: a job's stated requirement changes such that a
    previously-blocked user now clears it -> distinct 'became a match' alert,
    not a duplicate of the original (suppressed) notification."""
    job, profile, user, preference = _setup(db_session, jlpt_required=JLPTLevel.N2)
    profile.jlpt_level = JLPTLevel.N5
    db_session.flush()

    match_before = compute_match(db_session, profile, job, generate_explanation=False)
    assert match_before.deterministic_pass is False
    # Capture state *before* recomputing -- compute_match mutates and returns
    # the same Match row, so match_before would otherwise reflect the new
    # state too once match_after is computed (see app/services/match_service.py
    # for the production version of this pattern).
    previous_strength = match_before.match_strength
    previous_pass = match_before.deterministic_pass

    job.requirement.jlpt_requirement = JLPTLevel.N5
    db_session.flush()
    match_after = compute_match(db_session, profile, job, generate_explanation=False)
    assert match_after.deterministic_pass is True

    notification = maybe_notify(
        db_session,
        match_after,
        job,
        preference,
        previous_strength,
        previous_pass,
        user.email,
        "https://app/jobs/1",
    )
    assert notification is not None
    assert notification.type.value == "JOB_BECAME_MATCH"


def test_daily_notification_cap_is_respected(db_session):
    job, profile, user, preference = _setup(db_session, required_skills=["Python"])
    preference.max_notifications_per_day = 0
    db_session.flush()

    match = compute_match(db_session, profile, job, generate_explanation=False)
    notification = maybe_notify(db_session, match, job, preference, None, None, user.email, "https://app/jobs/1")
    assert notification is None


def test_below_threshold_score_does_not_notify(db_session):
    job, profile, user, preference = _setup(db_session, required_skills=["Kubernetes", "Go", "Rust"])
    preference.min_match_threshold = 0.9
    db_session.flush()

    match = compute_match(db_session, profile, job, generate_explanation=False)
    notification = maybe_notify(db_session, match, job, preference, None, None, user.email, "https://app/jobs/1")
    assert notification is None
