"""Stage 1 of the matching engine: deterministic, rule-based comparison of a
user's profile against a job's structured requirements. Produces a fully
transparent requirement-by-requirement breakdown (master spec section 13) --
never a bare percentage.
"""

from dataclasses import dataclass, field

from app.models.enums import JLPTLevel
from app.models.job import JobRequirement
from app.models.profile import Profile

_JLPT_ORDER = [JLPTLevel.NONE, JLPTLevel.N5, JLPTLevel.N4, JLPTLevel.N3, JLPTLevel.N2, JLPTLevel.N1]
_DEGREE_RANK = {"bachelor": 1, "master": 2, "phd": 3}


def _jlpt_index(level: JLPTLevel) -> int:
    return _JLPT_ORDER.index(level)


def _degree_rank(text: str) -> int:
    lowered = text.lower()
    for key, rank in _DEGREE_RANK.items():
        if key in lowered:
            return rank
    return 0


@dataclass
class RequirementRow:
    label: str
    category: str
    state: str
    detail: str


@dataclass
class DeterministicResult:
    rows: list[RequirementRow] = field(default_factory=list)
    hard_blockers_missing: int = 0
    required_skill_ratio: float = 1.0
    preferred_skill_ratio: float = 1.0


def _user_skill_names(profile: Profile) -> set[str]:
    return {us.skill.name.lower() for us in profile.skills if us.skill}


def evaluate(profile: Profile, requirement: JobRequirement, job_location: str | None, job_work_mode: str) -> DeterministicResult:
    result = DeterministicResult()
    user_skills = _user_skill_names(profile)

    if requirement.jlpt_requirement and requirement.jlpt_requirement != JLPTLevel.NONE:
        required_idx = _jlpt_index(requirement.jlpt_requirement)
        user_idx = _jlpt_index(profile.jlpt_level)
        if user_idx >= required_idx:
            state = "MATCH"
            detail = f"Meets stated requirement (you: {profile.jlpt_level.value})"
        elif user_idx == required_idx - 1:
            state = "PARTIAL"
            detail = f"Job asks for {requirement.jlpt_requirement.value}+, you have {profile.jlpt_level.value}"
            result.hard_blockers_missing += 0
        else:
            state = "MISSING"
            detail = f"Job asks for {requirement.jlpt_requirement.value}+, you have {profile.jlpt_level.value}"
            result.hard_blockers_missing += 1
        result.rows.append(RequirementRow(f"JLPT {requirement.jlpt_requirement.value}", "language", state, detail))
    elif requirement.japanese_requirement_raw:
        result.rows.append(
            RequirementRow("Japanese communication", "language", "UNKNOWN", requirement.japanese_requirement_raw)
        )

    if requirement.education_requirement:
        required_rank = _degree_rank(requirement.education_requirement)
        user_rank = max((_degree_rank(e.degree) for e in profile.education), default=0)
        if user_rank >= required_rank and required_rank > 0:
            state, detail = "MATCH", "Meets stated education requirement"
        elif profile.education:
            state, detail = "MISSING", f"Job requires {requirement.education_requirement}"
            result.hard_blockers_missing += 1
        else:
            state, detail = "UNKNOWN", "No education added to your profile yet"
        result.rows.append(RequirementRow(requirement.education_requirement, "education", state, detail))

    if requirement.minimum_experience_years is not None:
        required_years = requirement.minimum_experience_years
        user_years = profile.years_of_experience
        if user_years >= required_years or (profile.is_new_graduate and required_years <= 0.5):
            state, detail = "MATCH", f"You have {user_years:g} years"
        elif required_years - user_years <= 1:
            state, detail = "PARTIAL", f"Job asks for {required_years:g}+ years, you have {user_years:g}"
        else:
            state, detail = "MISSING", f"Job asks for {required_years:g}+ years, you have {user_years:g}"
        result.rows.append(RequirementRow(f"{required_years:g}+ years experience", "experience", state, detail))

    if requirement.required_skills:
        matched = 0
        for skill in requirement.required_skills:
            hit = skill.lower() in user_skills
            matched += 1 if hit else 0
            result.rows.append(
                RequirementRow(skill, "required_skill", "MATCH" if hit else "MISSING", "" if hit else "Not on your profile")
            )
        result.required_skill_ratio = matched / len(requirement.required_skills)

    if requirement.preferred_skills:
        matched = 0
        for skill in requirement.preferred_skills:
            hit = skill.lower() in user_skills
            matched += 1 if hit else 0
            result.rows.append(
                RequirementRow(
                    skill, "preferred_skill", "MATCH" if hit else "MISSING", "Preferred, not required" if not hit else ""
                )
            )
        result.preferred_skill_ratio = matched / len(requirement.preferred_skills)

    if requirement.new_graduate_allowed is False and profile.is_new_graduate:
        result.rows.append(
            RequirementRow(
                "New graduate eligibility", "eligibility", "MISSING", "This posting is for experienced candidates only"
            )
        )
        result.hard_blockers_missing += 1
    elif requirement.new_graduate_allowed is True and profile.is_new_graduate:
        result.rows.append(RequirementRow("New graduate eligibility", "eligibility", "MATCH", "New graduates welcome"))

    if profile.visa_sponsorship_required:
        if requirement.visa_sponsorship.value == "YES":
            state, detail = "MATCH", "Visa sponsorship is stated as available"
        elif requirement.visa_sponsorship.value == "NO":
            state, detail = "MISSING", "Visa sponsorship is stated as not available"
            result.hard_blockers_missing += 1
        else:
            state, detail = "UNKNOWN", "Not stated by the employer"
        result.rows.append(RequirementRow("Visa sponsorship", "visa", state, detail))

    if job_location and profile.preferred_japan_locations and job_work_mode != "REMOTE":
        overlap = any(loc.lower() in job_location.lower() for loc in profile.preferred_japan_locations)
        result.rows.append(
            RequirementRow(
                job_location,
                "location",
                "MATCH" if overlap else "PARTIAL",
                "Matches your preferred locations" if overlap else "Outside your stated preferred locations",
            )
        )

    return result
