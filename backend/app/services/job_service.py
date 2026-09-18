from dataclasses import dataclass

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.enums import EmploymentType, JobStatus, WorkMode
from app.models.interaction import Match
from app.models.job import Job, JobRequirement


@dataclass
class JobFilters:
    search: str | None = None
    location: str | None = None
    company_id: str | None = None
    employment_type: EmploymentType | None = None
    work_mode: WorkMode | None = None
    only_verified_active: bool = False
    new_graduate: bool | None = None
    visa_sponsorship: bool | None = None
    skill: str | None = None
    jlpt_max: str | None = None  # e.g. "N3" means jobs requiring N3 or easier (or unstated)
    sort: str = "recently_verified"  # recently_verified | recently_posted | salary_desc
    page: int = 1
    page_size: int = 20


def list_jobs(db: Session, filters: JobFilters, user_id: str | None = None) -> tuple[list[Job], int]:
    query = db.query(Job).options(joinedload(Job.company), joinedload(Job.requirement))

    if filters.search:
        like = f"%{filters.search}%"
        query = query.join(Job.company).filter(
            or_(Job.title.ilike(like), Job.location.ilike(like), Job.original_description.ilike(like))
        )
    if filters.location:
        query = query.filter(Job.location.ilike(f"%{filters.location}%"))
    if filters.company_id:
        query = query.filter(Job.company_id == filters.company_id)
    if filters.employment_type:
        query = query.filter(Job.employment_type == filters.employment_type)
    if filters.work_mode:
        query = query.filter(Job.work_mode == filters.work_mode)
    if filters.only_verified_active:
        query = query.filter(Job.status == JobStatus.ACTIVE)

    if filters.new_graduate is not None or filters.visa_sponsorship is not None or filters.skill:
        query = query.join(JobRequirement, Job.requirement)
        if filters.new_graduate is not None:
            query = query.filter(JobRequirement.new_graduate_allowed == filters.new_graduate)
        if filters.visa_sponsorship:
            query = query.filter(JobRequirement.visa_sponsorship == "YES")
        if filters.skill:
            like_skill = f"%{filters.skill}%"
            # SQLite JSON columns are stored as text; a simple LIKE over the
            # serialized list is sufficient for this scale and avoids a
            # separate join table just for filtering.
            from sqlalchemy import cast, String

            query = query.filter(
                or_(
                    cast(JobRequirement.required_skills, String).ilike(like_skill),
                    cast(JobRequirement.preferred_skills, String).ilike(like_skill),
                )
            )

    total = query.count()

    if filters.sort == "recently_posted":
        query = query.order_by(Job.first_seen_at.desc())
    elif filters.sort == "salary_desc":
        query = query.order_by(Job.salary_max.desc().nullslast())
    else:
        query = query.order_by(Job.last_verified_at.desc().nullslast())

    items = query.offset((filters.page - 1) * filters.page_size).limit(filters.page_size).all()

    if user_id:
        job_ids = [j.id for j in items]
        matches = {
            m.job_id: m for m in db.query(Match).filter(Match.user_id == user_id, Match.job_id.in_(job_ids)).all()
        }
        for job in items:
            match = matches.get(job.id)
            job.match_score = match.overall_score if match else None
            job.match_strength = match.match_strength.value if match else None
    else:
        for job in items:
            job.match_score = None
            job.match_strength = None

    return items, total
