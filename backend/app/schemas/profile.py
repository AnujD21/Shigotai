from pydantic import BaseModel, Field

from app.models.enums import EmploymentType, JapaneseLevel, JLPTLevel, WorkMode


class EducationIn(BaseModel):
    id: str | None = None
    degree: str
    university: str
    field_of_study: str | None = None
    graduation_year: int | None = None
    is_current_student: bool = False


class ExperienceIn(BaseModel):
    id: str | None = None
    company_name: str
    role: str
    is_internship: bool = False
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None


class ProjectIn(BaseModel):
    id: str | None = None
    name: str
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)
    role: str | None = None
    github_url: str | None = None
    project_url: str | None = None
    duration: str | None = None


class CertificationIn(BaseModel):
    id: str | None = None
    name: str
    issuer: str | None = None
    year: int | None = None


class SkillIn(BaseModel):
    name: str
    proficiency: str | None = None
    years_experience: float | None = None
    is_ai_ml: bool = False


class ProfileUpdate(BaseModel):
    country: str | None = None
    current_location: str | None = None
    preferred_japan_locations: list[str] | None = None
    years_of_experience: float | None = None
    is_new_graduate: bool | None = None

    jlpt_level: JLPTLevel | None = None
    japanese_speaking_level: JapaneseLevel | None = None
    japanese_reading_level: JapaneseLevel | None = None
    japanese_writing_level: JapaneseLevel | None = None
    business_japanese_ability: JapaneseLevel | None = None
    english_level: JapaneseLevel | None = None

    desired_roles: list[str] | None = None
    work_mode_preference: WorkMode | None = None
    employment_type_preference: EmploymentType | None = None
    salary_expectation_min: int | None = None
    salary_expectation_max: int | None = None
    company_size_preference: str | None = None
    industry_preference: list[str] | None = None
    visa_sponsorship_required: bool | None = None

    education: list[EducationIn] | None = None
    experience: list[ExperienceIn] | None = None
    projects: list[ProjectIn] | None = None
    certifications: list[CertificationIn] | None = None
    skills: list[SkillIn] | None = None


class ProfileOut(BaseModel):
    id: str
    user_id: str
    country: str | None
    current_location: str | None
    preferred_japan_locations: list[str]
    years_of_experience: float
    is_new_graduate: bool

    jlpt_level: JLPTLevel
    japanese_speaking_level: JapaneseLevel
    japanese_reading_level: JapaneseLevel
    japanese_writing_level: JapaneseLevel
    business_japanese_ability: JapaneseLevel
    english_level: JapaneseLevel

    desired_roles: list[str]
    work_mode_preference: WorkMode
    employment_type_preference: EmploymentType
    salary_expectation_min: int | None
    salary_expectation_max: int | None
    company_size_preference: str | None
    industry_preference: list[str]
    visa_sponsorship_required: bool

    resume_original_filename: str | None

    education: list[EducationIn]
    experience: list[ExperienceIn]
    projects: list[ProjectIn]
    certifications: list[CertificationIn]
    skills: list[SkillIn]

    completeness_percent: int
    completeness_suggestions: list[str]

    model_config = {"from_attributes": True}


class ResumeExtractionResult(BaseModel):
    education: list[EducationIn]
    experience: list[ExperienceIn]
    projects: list[ProjectIn]
    certifications: list[CertificationIn]
    skills: list[SkillIn]
    jlpt_level: JLPTLevel | None = None
    source_filename: str
    warnings: list[str] = Field(default_factory=list)
