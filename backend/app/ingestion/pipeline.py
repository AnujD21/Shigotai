"""SOURCE -> INGESTION -> NORMALIZATION -> AI EXTRACTION -> DEDUPLICATION ->
JOB DATABASE -> ACTIVE-JOB VERIFICATION, as laid out in master spec section 6.
Matching + notifications are triggered separately per-user (section 15) so a
single ingestion run stays fast and idempotent.
"""

import hashlib
import re
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.ingestion.base import JobSourceAdapter, RawJobPosting
from app.models.company import Company
from app.models.enums import JobStatus
from app.models.job import Job, JobSource, JobVerification
from app.services.extraction_service import extract_job_requirements


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _content_hash(raw: RawJobPosting) -> str:
    return hashlib.sha256(f"{raw.title}\n{raw.description}".encode("utf-8")).hexdigest()


def _get_or_create_source(db: Session, adapter: JobSourceAdapter) -> JobSource:
    source = db.query(JobSource).filter(JobSource.name == adapter.source_name).first()
    if source is None:
        source = JobSource(name=adapter.source_name, source_type=adapter.source_type, is_active=True)
        db.add(source)
        db.flush()
    source.last_polled_at = datetime.now(timezone.utc)
    return source


def _get_or_create_company(db: Session, raw: RawJobPosting) -> Company:
    company = db.query(Company).filter(Company.name == raw.company_name).first()
    if company is None:
        company = Company(
            name=raw.company_name,
            slug=slugify(raw.company_name),
            website=raw.company_website,
            industry=raw.industry,
        )
        db.add(company)
        db.flush()
    return company


def _find_duplicate(db: Session, company: Company, raw: RawJobPosting, source: JobSource) -> Job | None:
    # Primary dedup key: same source + source_job_id.
    by_source_id = (
        db.query(Job)
        .filter(Job.source_id == source.id, Job.source_job_id == raw.source_job_id)
        .first()
    )
    if by_source_id:
        return by_source_id

    # Cross-source dedup fallback: same company + normalized title + location,
    # which catches the same opening posted on a company page and an ATS.
    normalized_title = raw.title.strip().lower()
    candidates = db.query(Job).filter(Job.company_id == company.id).all()
    for candidate in candidates:
        if candidate.title.strip().lower() == normalized_title and (candidate.location or "") == (raw.location or ""):
            return candidate
    return None


def ingest_source(db: Session, adapter: JobSourceAdapter, is_demo: bool = False) -> list[Job]:
    source = _get_or_create_source(db, adapter)
    now = datetime.now(timezone.utc)
    ingested: list[Job] = []

    for raw in adapter.fetch_jobs():
        company = _get_or_create_company(db, raw)
        duplicate = _find_duplicate(db, company, raw, source)
        new_hash = _content_hash(raw)

        if duplicate:
            job = duplicate
            content_changed = job.content_hash != new_hash
            job.title = raw.title
            job.original_description = raw.description
            job.description_language = raw.description_language
            job.location = raw.location
            job.salary_min = raw.salary_min
            job.salary_max = raw.salary_max
            job.salary_currency = raw.salary_currency
            job.employment_type = raw.employment_type
            job.work_mode = raw.work_mode
            job.application_deadline = raw.application_deadline
            job.content_hash = new_hash
            job.last_verified_at = now
            job.status = JobStatus.ACTIVE
            db.add(JobVerification(job_id=job.id, checked_at=now, status_found=JobStatus.ACTIVE, evidence="Re-seen in source feed"))
        else:
            content_changed = True
            job = Job(
                company_id=company.id,
                source_id=source.id,
                title=raw.title,
                original_description=raw.description,
                description_language=raw.description_language,
                source_url=raw.source_url,
                source_job_id=raw.source_job_id,
                canonical_url=raw.canonical_url,
                content_hash=new_hash,
                location=raw.location,
                salary_min=raw.salary_min,
                salary_max=raw.salary_max,
                salary_currency=raw.salary_currency,
                employment_type=raw.employment_type,
                work_mode=raw.work_mode,
                application_deadline=raw.application_deadline,
                first_seen_at=now,
                last_verified_at=now,
                status=JobStatus.ACTIVE,
                is_demo_data=is_demo,
            )
            db.add(job)
            db.flush()
            db.add(JobVerification(job_id=job.id, checked_at=now, status_found=JobStatus.ACTIVE, evidence="First seen in source feed"))

        if content_changed:
            extract_job_requirements(db, job, force=True)

        db.flush()
        ingested.append(job)

    db.commit()
    return ingested


def verify_job_status(db: Session, adapter: JobSourceAdapter, job: Job) -> Job:
    """Re-check a single job against its source (master spec section 11)."""
    if not job.source_job_id:
        return job
    status = adapter.check_status(job.source_job_id)
    now = datetime.now(timezone.utc)
    job.status = status
    job.last_verified_at = now
    db.add(JobVerification(job_id=job.id, checked_at=now, status_found=status, evidence="Scheduled re-verification"))
    db.commit()
    return job
