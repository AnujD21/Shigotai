from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin, utcnow
from app.models.enums import (
    EmploymentType,
    JapaneseLevel,
    JLPTLevel,
    JobStatus,
    VisaSponsorship,
    WorkMode,
)


class JobSource(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "job_sources"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(60), nullable=False)
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    respects_robots_txt: Mapped[bool] = mapped_column(Boolean, default=True)
    rate_limit_per_minute: Mapped[int] = mapped_column(Integer, default=30)
    last_polled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    jobs: Mapped[list["Job"]] = relationship(back_populates="source")


class Job(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "jobs"

    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    source_id: Mapped[str] = mapped_column(ForeignKey("job_sources.id", ondelete="SET NULL"), nullable=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    original_description: Mapped[str] = mapped_column(Text, nullable=False)
    description_language: Mapped[str] = mapped_column(String(10), default="en")

    source_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    source_job_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    canonical_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)

    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str | None] = mapped_column(String(10), nullable=True)

    employment_type: Mapped[EmploymentType] = mapped_column(Enum(EmploymentType), default=EmploymentType.FULL_TIME)
    work_mode: Mapped[WorkMode] = mapped_column(Enum(WorkMode), default=WorkMode.UNKNOWN)

    application_deadline: Mapped[str | None] = mapped_column(String(20), nullable=True)

    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    last_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.UNKNOWN, index=True)

    is_demo_data: Mapped[bool] = mapped_column(Boolean, default=False)

    company: Mapped["Company"] = relationship(back_populates="jobs")
    source: Mapped["JobSource"] = relationship(back_populates="jobs")
    requirement: Mapped["JobRequirement"] = relationship(
        back_populates="job", uselist=False, cascade="all, delete-orphan"
    )
    embedding: Mapped["JobEmbedding"] = relationship(
        back_populates="job", uselist=False, cascade="all, delete-orphan"
    )
    verifications: Mapped[list["JobVerification"]] = relationship(
        back_populates="job", cascade="all, delete-orphan", order_by="desc(JobVerification.checked_at)"
    )


class JobRequirement(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "job_requirements"

    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), unique=True, nullable=False)

    required_skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    preferred_skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    education_requirement: Mapped[str | None] = mapped_column(String(255), nullable=True)
    minimum_experience_years: Mapped[float | None] = mapped_column(Float, nullable=True)

    jlpt_requirement: Mapped[JLPTLevel | None] = mapped_column(Enum(JLPTLevel), nullable=True)
    japanese_requirement_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    japanese_requirement_level: Mapped[JapaneseLevel | None] = mapped_column(Enum(JapaneseLevel), nullable=True)
    english_requirement_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    english_requirement_level: Mapped[JapaneseLevel | None] = mapped_column(Enum(JapaneseLevel), nullable=True)

    visa_sponsorship: Mapped[VisaSponsorship] = mapped_column(Enum(VisaSponsorship), default=VisaSponsorship.NOT_STATED)
    new_graduate_allowed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    internship_eligible: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    extraction_source: Mapped[str] = mapped_column(String(20), default="RULE_BASED")
    extraction_confidence: Mapped[float] = mapped_column(Float, default=0.5)
    extracted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    raw_extraction_json: Mapped[dict] = mapped_column(JSON, default=dict)

    job: Mapped["Job"] = relationship(back_populates="requirement")


class JobEmbedding(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "job_embeddings"

    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), unique=True, nullable=False)
    model_name: Mapped[str] = mapped_column(String(120), default="tfidf-v1")
    vector: Mapped[list[float]] = mapped_column(JSON, default=list)
    source_text_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    job: Mapped["Job"] = relationship(back_populates="embedding")


class JobVerification(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "job_verification"

    job_id: Mapped[str] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    status_found: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.UNKNOWN)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)

    job: Mapped["Job"] = relationship(back_populates="verifications")
