from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.models.enums import EmploymentType, JobStatus, WorkMode


@dataclass
class RawJobPosting:
    company_name: str
    company_website: str | None
    title: str
    description: str
    description_language: str
    source_job_id: str
    source_url: str
    canonical_url: str
    location: str | None
    employment_type: EmploymentType
    work_mode: WorkMode
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str | None = None
    application_deadline: str | None = None
    industry: str | None = None


class JobSourceAdapter(ABC):
    """Uniform interface every job source implements, whether it's a demo
    dataset, an ATS API (Greenhouse, Lever), or an authorized feed. The rest
    of the ingestion pipeline (normalization, extraction, dedup, matching)
    never needs to know which adapter produced a posting -- see master spec
    section 49.
    """

    source_name: str
    source_type: str

    @abstractmethod
    def fetch_jobs(self) -> list[RawJobPosting]:
        """Return currently-listed postings from this source."""

    @abstractmethod
    def check_status(self, source_job_id: str) -> JobStatus:
        """Re-check a single posting's status against the source of truth."""
