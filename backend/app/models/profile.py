from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import EmploymentType, JapaneseLevel, JLPTLevel, SkillCategory, WorkMode


class Profile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "profiles"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    country: Mapped[str | None] = mapped_column(String(120), nullable=True)
    current_location: Mapped[str | None] = mapped_column(String(120), nullable=True)
    preferred_japan_locations: Mapped[list[str]] = mapped_column(JSON, default=list)

    years_of_experience: Mapped[float] = mapped_column(Float, default=0)
    is_new_graduate: Mapped[bool] = mapped_column(Boolean, default=False)

    jlpt_level: Mapped[JLPTLevel] = mapped_column(Enum(JLPTLevel), default=JLPTLevel.NONE)
    japanese_speaking_level: Mapped[JapaneseLevel] = mapped_column(Enum(JapaneseLevel), default=JapaneseLevel.NONE)
    japanese_reading_level: Mapped[JapaneseLevel] = mapped_column(Enum(JapaneseLevel), default=JapaneseLevel.NONE)
    japanese_writing_level: Mapped[JapaneseLevel] = mapped_column(Enum(JapaneseLevel), default=JapaneseLevel.NONE)
    business_japanese_ability: Mapped[JapaneseLevel] = mapped_column(Enum(JapaneseLevel), default=JapaneseLevel.NONE)
    english_level: Mapped[JapaneseLevel] = mapped_column(Enum(JapaneseLevel), default=JapaneseLevel.NONE)

    desired_roles: Mapped[list[str]] = mapped_column(JSON, default=list)
    work_mode_preference: Mapped[WorkMode] = mapped_column(Enum(WorkMode), default=WorkMode.UNKNOWN)
    employment_type_preference: Mapped[EmploymentType] = mapped_column(
        Enum(EmploymentType), default=EmploymentType.FULL_TIME
    )
    salary_expectation_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_expectation_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    company_size_preference: Mapped[str | None] = mapped_column(String(40), nullable=True)
    industry_preference: Mapped[list[str]] = mapped_column(JSON, default=list)
    visa_sponsorship_required: Mapped[bool] = mapped_column(Boolean, default=False)

    resume_file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    resume_original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user: Mapped["User"] = relationship(back_populates="profile")
    education: Mapped[list["Education"]] = relationship(back_populates="profile", cascade="all, delete-orphan")
    experience: Mapped[list["Experience"]] = relationship(back_populates="profile", cascade="all, delete-orphan")
    projects: Mapped[list["Project"]] = relationship(back_populates="profile", cascade="all, delete-orphan")
    certifications: Mapped[list["Certification"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )
    skills: Mapped[list["UserSkill"]] = relationship(back_populates="profile", cascade="all, delete-orphan")


class Education(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "education"

    profile_id: Mapped[str] = mapped_column(ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    degree: Mapped[str] = mapped_column(String(120), nullable=False)
    university: Mapped[str] = mapped_column(String(255), nullable=False)
    field_of_study: Mapped[str | None] = mapped_column(String(255), nullable=True)
    graduation_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_current_student: Mapped[bool] = mapped_column(Boolean, default=False)

    profile: Mapped[Profile] = relationship(back_populates="education")


class Experience(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "experience"

    profile_id: Mapped[str] = mapped_column(ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(255), nullable=False)
    is_internship: Mapped[bool] = mapped_column(Boolean, default=False)
    start_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    end_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    profile: Mapped[Profile] = relationship(back_populates="experience")


class Project(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    profile_id: Mapped[str] = mapped_column(ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    technologies: Mapped[list[str]] = mapped_column(JSON, default=list)
    role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    project_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    duration: Mapped[str | None] = mapped_column(String(120), nullable=True)

    profile: Mapped[Profile] = relationship(back_populates="projects")


class Certification(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "certifications"

    profile_id: Mapped[str] = mapped_column(ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    issuer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    profile: Mapped[Profile] = relationship(back_populates="certifications")


class Skill(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "skills"

    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    category: Mapped[SkillCategory] = mapped_column(Enum(SkillCategory), default=SkillCategory.OTHER)
    aliases: Mapped[list[str]] = mapped_column(JSON, default=list)


class UserSkill(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "user_skills"

    profile_id: Mapped[str] = mapped_column(ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[str] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    proficiency: Mapped[str | None] = mapped_column(String(40), nullable=True)
    years_experience: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_ai_ml: Mapped[bool] = mapped_column(Boolean, default=False)

    profile: Mapped[Profile] = relationship(back_populates="skills")
    skill: Mapped[Skill] = relationship()
