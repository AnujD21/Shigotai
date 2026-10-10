"""Pydantic shapes every LLM provider must return.

Defined once so the Anthropic provider can hand them to structured outputs
and the OpenAI-compatible provider can validate free-form JSON against the
exact same contract. Nullable fields are required-but-nullable on purpose:
the model has to state "unknown" explicitly instead of silently omitting.
"""

from typing import Literal

from pydantic import BaseModel, Field


class JobRequirementsLLM(BaseModel):
    required_skills: list[str]
    preferred_skills: list[str]
    minimum_experience: float | None
    education_requirement: str | None
    jlpt_requirement: Literal["N1", "N2", "N3", "N4", "N5"] | None
    japanese_requirement: str | None
    english_requirement: str | None
    new_graduate_allowed: bool | None
    visa_sponsorship: Literal["YES", "NO", "NOT_STATED"]


class ResumeEducationLLM(BaseModel):
    degree: str
    university: str
    field_of_study: str | None
    graduation_year: int | None
    is_current_student: bool


class ResumeExperienceLLM(BaseModel):
    company_name: str
    role: str
    is_internship: bool
    start_date: str | None = Field(description="YYYY-MM, or YYYY when the month isn't given")
    end_date: str | None = Field(description="YYYY-MM or YYYY; null when this is the current role")
    description: str | None


class ResumeProjectLLM(BaseModel):
    name: str
    description: str | None
    technologies: list[str]
    github_url: str | None
    project_url: str | None


class ResumeCertificationLLM(BaseModel):
    name: str
    issuer: str | None
    year: int | None


class ResumeLLMExtraction(BaseModel):
    education: list[ResumeEducationLLM]
    experience: list[ResumeExperienceLLM]
    projects: list[ResumeProjectLLM]
    certifications: list[ResumeCertificationLLM]
    skills: list[str]
    jlpt_level: Literal["N1", "N2", "N3", "N4", "N5"] | None
    total_years_of_experience: float | None
