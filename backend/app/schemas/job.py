from datetime import datetime

from pydantic import BaseModel

from app.models.enums import EmploymentType, JapaneseLevel, JLPTLevel, JobStatus, VisaSponsorship, WorkMode


class CompanySummary(BaseModel):
    id: str
    name: str
    slug: str
    industry: str | None
    headquarters_location: str | None
    website: str | None
    logo_url: str | None

    model_config = {"from_attributes": True}


class JobRequirementOut(BaseModel):
    required_skills: list[str]
    preferred_skills: list[str]
    education_requirement: str | None
    minimum_experience_years: float | None
    jlpt_requirement: JLPTLevel | None
    japanese_requirement_raw: str | None
    japanese_requirement_level: JapaneseLevel | None
    english_requirement_raw: str | None
    english_requirement_level: JapaneseLevel | None
    visa_sponsorship: VisaSponsorship
    new_graduate_allowed: bool | None
    internship_eligible: bool | None
    extraction_source: str
    extraction_confidence: float

    model_config = {"from_attributes": True}


class JobCard(BaseModel):
    id: str
    title: str
    company: CompanySummary
    location: str | None
    employment_type: EmploymentType
    work_mode: WorkMode
    salary_min: int | None
    salary_max: int | None
    salary_currency: str | None
    status: JobStatus
    last_verified_at: datetime | None
    first_seen_at: datetime
    is_demo_data: bool
    requirement: JobRequirementOut | None
    match_score: float | None = None
    match_strength: str | None = None

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    items: list[JobCard]
    total: int
    page: int
    page_size: int


class JobDetail(JobCard):
    original_description: str
    description_language: str
    source_url: str
    canonical_url: str
    application_deadline: str | None
