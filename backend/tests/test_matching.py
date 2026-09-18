from app.matching.deterministic import evaluate
from app.matching.engine import compute_match
from app.models.company import Company
from app.models.enums import EmploymentType, JLPTLevel, VisaSponsorship, WorkMode
from app.models.job import Job, JobRequirement
from app.models.profile import Profile, UserSkill
from app.models.user import User
from app.services.profile_service import get_or_create_skill


def _make_job(db, **overrides):
    company = Company(name="Test Co", slug="test-co")
    db.add(company)
    db.flush()
    defaults = dict(
        company_id=company.id,
        title="AI Engineer",
        original_description="desc",
        source_url="https://example.com/1",
        canonical_url="https://example.com/1",
        content_hash="abc",
        location="Tokyo",
        employment_type=EmploymentType.FULL_TIME,
        work_mode=WorkMode.HYBRID,
    )
    defaults.update(overrides)
    job = Job(**defaults)
    db.add(job)
    db.flush()
    return job


def _make_profile(db, jlpt=JLPTLevel.NONE, years=0.0, skills=None, is_new_graduate=False):
    user = User(email=f"user-{id(object())}@example.com", hashed_password="x", full_name="Test User")
    db.add(user)
    db.flush()
    profile = Profile(user_id=user.id, jlpt_level=jlpt, years_of_experience=years, is_new_graduate=is_new_graduate)
    db.add(profile)
    db.flush()
    for skill_name in skills or []:
        skill = get_or_create_skill(db, skill_name)
        profile.skills.append(UserSkill(profile_id=profile.id, skill_id=skill.id))
    db.flush()
    return profile


def test_jlpt_exact_match_is_match(db_session):
    job = _make_job(db_session)
    requirement = JobRequirement(job_id=job.id, jlpt_requirement=JLPTLevel.N3)
    db_session.add(requirement)
    db_session.flush()
    profile = _make_profile(db_session, jlpt=JLPTLevel.N3)

    result = evaluate(profile, requirement, job.location, job.work_mode.value)
    jlpt_row = next(r for r in result.rows if r.category == "language")
    assert jlpt_row.state == "MATCH"


def test_jlpt_one_level_below_is_partial_not_missing(db_session):
    """Master spec section 13 example: job wants N2, user has N3 -> shown as
    a partial/warning, not a hard rejection."""
    job = _make_job(db_session)
    requirement = JobRequirement(job_id=job.id, jlpt_requirement=JLPTLevel.N2)
    db_session.add(requirement)
    db_session.flush()
    profile = _make_profile(db_session, jlpt=JLPTLevel.N3)

    result = evaluate(profile, requirement, job.location, job.work_mode.value)
    jlpt_row = next(r for r in result.rows if r.category == "language")
    assert jlpt_row.state == "PARTIAL"
    assert result.hard_blockers_missing == 0


def test_jlpt_far_below_requirement_is_missing_and_blocks(db_session):
    job = _make_job(db_session)
    requirement = JobRequirement(job_id=job.id, jlpt_requirement=JLPTLevel.N1)
    db_session.add(requirement)
    db_session.flush()
    profile = _make_profile(db_session, jlpt=JLPTLevel.N5)

    result = evaluate(profile, requirement, job.location, job.work_mode.value)
    jlpt_row = next(r for r in result.rows if r.category == "language")
    assert jlpt_row.state == "MISSING"
    assert result.hard_blockers_missing == 1


def test_unspecified_jlpt_never_invents_a_level(db_session):
    """The extraction pipeline must never turn a vague 'business Japanese'
    requirement into a specific JLPT level (master spec section 50)."""
    job = _make_job(db_session)
    requirement = JobRequirement(job_id=job.id, jlpt_requirement=None, japanese_requirement_raw="Business-level Japanese communication required")
    db_session.add(requirement)
    db_session.flush()
    profile = _make_profile(db_session, jlpt=JLPTLevel.N3)

    result = evaluate(profile, requirement, job.location, job.work_mode.value)
    japanese_row = next(r for r in result.rows if r.category == "language")
    assert japanese_row.state == "UNKNOWN"


def test_required_skill_gap_is_reported_not_hidden(db_session):
    job = _make_job(db_session)
    requirement = JobRequirement(job_id=job.id, required_skills=["Python", "AWS"])
    db_session.add(requirement)
    db_session.flush()
    profile = _make_profile(db_session, skills=["Python"])

    result = evaluate(profile, requirement, job.location, job.work_mode.value)
    labels = {(r.label, r.state) for r in result.rows}
    assert ("Python", "MATCH") in labels
    assert ("AWS", "MISSING") in labels
    assert result.required_skill_ratio == 0.5


def test_new_graduate_ineligibility_blocks_deterministic_pass(db_session):
    job = _make_job(db_session)
    requirement = JobRequirement(job_id=job.id, new_graduate_allowed=False)
    db_session.add(requirement)
    db_session.flush()
    profile = _make_profile(db_session, is_new_graduate=True)

    result = evaluate(profile, requirement, job.location, job.work_mode.value)
    assert result.hard_blockers_missing == 1


def test_visa_sponsorship_not_stated_is_unknown_not_missing(db_session):
    job = _make_job(db_session)
    requirement = JobRequirement(job_id=job.id, visa_sponsorship=VisaSponsorship.NOT_STATED)
    db_session.add(requirement)
    db_session.flush()
    profile = _make_profile(db_session)
    profile.visa_sponsorship_required = True

    result = evaluate(profile, requirement, job.location, job.work_mode.value)
    visa_row = next(r for r in result.rows if r.category == "visa")
    assert visa_row.state == "UNKNOWN"


def test_compute_match_strong_when_everything_lines_up(db_session):
    job = _make_job(
        db_session,
        title="Backend Engineer",
        original_description="We need a backend engineer with strong Python and Docker experience.",
    )
    requirement = JobRequirement(
        job_id=job.id,
        required_skills=["Python", "Docker"],
        jlpt_requirement=JLPTLevel.N3,
    )
    db_session.add(requirement)
    db_session.flush()
    job.requirement = requirement

    profile = _make_profile(db_session, jlpt=JLPTLevel.N2, years=3, skills=["Python", "Docker"])

    match = compute_match(db_session, profile, job, generate_explanation=False)
    assert match.deterministic_pass is True
    assert match.match_strength.value == "STRONG_MATCH"


def test_compute_match_significant_gaps_when_nothing_lines_up(db_session):
    job = _make_job(db_session, title="Backend Engineer")
    requirement = JobRequirement(
        job_id=job.id,
        required_skills=["Kubernetes", "Go"],
        jlpt_requirement=JLPTLevel.N1,
    )
    db_session.add(requirement)
    db_session.flush()
    job.requirement = requirement

    profile = _make_profile(db_session, jlpt=JLPTLevel.NONE, years=0, skills=[])

    match = compute_match(db_session, profile, job, generate_explanation=False)
    assert match.match_strength.value == "SIGNIFICANT_GAPS"
