from pydantic import BaseModel

from app.schemas.job import JobCard


class CompanyOut(BaseModel):
    id: str
    name: str
    slug: str
    industry: str | None
    headquarters_location: str | None
    website: str | None
    logo_url: str | None
    description: str | None
    size_band: str | None
    tags: list[str]

    model_config = {"from_attributes": True}


class CompatibilityBand(BaseModel):
    label: str
    band: str  # STRONG | GOOD | LIMITED | UNKNOWN
    detail: str


class CompanyDetail(CompanyOut):
    open_positions: list[JobCard]
    compatibility: list[CompatibilityBand] | None = None


class SavedJobOut(BaseModel):
    id: str
    job: JobCard
    saved_at: str
    application_status: str | None = None


class ApplicationOut(BaseModel):
    id: str
    job: JobCard
    status: str
    applied_at: str | None
    status_updated_at: str
    notes: str | None
