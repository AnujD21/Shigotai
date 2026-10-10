"""Live job sources: the public job-board APIs of applicant tracking systems.

Greenhouse, Lever, Ashby, and SmartRecruiters each publish a free,
unauthenticated JSON API for exactly this purpose -- it's what powers the
companies' own careers pages. Using them means:

- no API key, no scraping, no Terms-of-Service gray area;
- full descriptions straight from the employer (no aggregator snippets);
- exact "still hiring" signals: when a posting disappears from the board,
  the role is closed (see `close_missing` in pipeline.ingest_source).

Each adapter covers one company's board and keeps only roles located in
Japan. The boards to poll live in japan_boards.py.
"""

import logging
import re
from abc import abstractmethod
from typing import Any

import httpx

from app.ingestion.base import JobSourceAdapter, RawJobPosting
from app.ingestion.text import detect_language, html_to_text
from app.models.enums import EmploymentType, JobStatus, WorkMode

logger = logging.getLogger(__name__)

USER_AGENT = "ShigotaiJobBot/1.0 (+https://github.com/shigotai; job-board API client)"
_TIMEOUT = httpx.Timeout(30.0, connect=10.0)

_JAPAN_PATTERN = re.compile(
    r"\b(japan|tokyo|osaka|kyoto|yokohama|nagoya|fukuoka|sapporo|kobe|sendai|kawasaki|saitama|chiba|"
    r"kanagawa|aichi|hyogo|tsukuba)\b|日本|東京|大阪|京都|横浜|名古屋|福岡|札幌|神戸|仙台|川崎|神奈川|埼玉|千葉|愛知|兵庫",
    re.IGNORECASE,
)


def is_japan_location(*values: str | None) -> bool:
    return any(value and _JAPAN_PATTERN.search(value) for value in values)


def infer_employment_type(*signals: str | None) -> EmploymentType:
    text = " ".join(s for s in signals if s).lower()
    if re.search(r"\bintern(ship)?\b|インターン", text):
        return EmploymentType.INTERNSHIP
    if re.search(r"new grad|graduate program|新卒", text):
        return EmploymentType.NEW_GRADUATE
    if re.search(r"\bcontract(or)?\b|\btemporary\b|契約|派遣", text):
        return EmploymentType.CONTRACT
    return EmploymentType.FULL_TIME


def infer_work_mode(*signals: str | None) -> WorkMode:
    text = " ".join(s for s in signals if s).lower()
    if "hybrid" in text or "ハイブリッド" in text:
        return WorkMode.HYBRID
    if "remote" in text or "リモート" in text:
        return WorkMode.REMOTE
    if re.search(r"on[- ]?site|in[- ]office|出社", text):
        return WorkMode.ONSITE
    return WorkMode.UNKNOWN


class ATSJobSource(JobSourceAdapter):
    """One company's board on one ATS."""

    platform: str
    source_type: str

    def __init__(self, slug: str, company_name: str, company_website: str | None = None, industry: str | None = None):
        self.slug = slug
        self.company_name = company_name
        self.company_website = company_website
        self.industry = industry
        self.source_name = f"{self.platform}:{slug}"

    def _get(self, url: str, params: dict | None = None) -> Any:
        response = httpx.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=_TIMEOUT)
        response.raise_for_status()
        return response.json()

    def _posting(self, **fields) -> RawJobPosting:
        description = fields.pop("description")
        return RawJobPosting(
            company_name=self.company_name,
            company_website=self.company_website,
            industry=self.industry,
            description=description,
            description_language=detect_language(description),
            **fields,
        )

    def _status_from_url(self, url: str) -> JobStatus:
        try:
            response = httpx.get(url, headers={"User-Agent": USER_AGENT}, timeout=_TIMEOUT)
        except httpx.HTTPError:
            return JobStatus.UNKNOWN
        if response.status_code == 404:
            return JobStatus.CLOSED
        if response.status_code == 200:
            return JobStatus.ACTIVE
        return JobStatus.UNKNOWN

    @abstractmethod
    def fetch_jobs(self) -> list[RawJobPosting]: ...


class GreenhouseSource(ATSJobSource):
    """https://developers.greenhouse.io/job-board.html"""

    platform = "greenhouse"
    source_type = "ATS_GREENHOUSE"
    _BASE = "https://boards-api.greenhouse.io/v1/boards"

    def fetch_jobs(self) -> list[RawJobPosting]:
        data = self._get(f"{self._BASE}/{self.slug}/jobs", params={"content": "true"})
        postings = []
        for job in data.get("jobs", []):
            raw_location = location = (job.get("location") or {}).get("name")
            # Office names ("Tokyo, Japan") read better than their address-like
            # locations ("Japan, 東京都東京都"); check both, display the name first.
            offices = [v for o in job.get("offices") or [] for v in (o.get("name"), o.get("location")) if v]
            if not is_japan_location(location, *offices):
                continue
            if not is_japan_location(location):
                # Some boards put the work mode in the location field
                # ("Hybrid") and the city only on the office.
                location = next(office for office in offices if is_japan_location(office))
            metadata = " ".join(str(m.get("value") or "") for m in job.get("metadata") or [])
            departments = " ".join(d.get("name") or "" for d in job.get("departments") or [])
            postings.append(
                self._posting(
                    title=job["title"].strip(),
                    description=html_to_text(job.get("content")),
                    source_job_id=str(job["id"]),
                    source_url=job["absolute_url"],
                    canonical_url=job["absolute_url"],
                    location=location,
                    employment_type=infer_employment_type(job["title"], departments),
                    work_mode=infer_work_mode(metadata, raw_location),
                    application_deadline=job.get("application_deadline"),
                )
            )
        return postings

    def check_status(self, source_job_id: str) -> JobStatus:
        return self._status_from_url(f"{self._BASE}/{self.slug}/jobs/{source_job_id}")


class LeverSource(ATSJobSource):
    """https://github.com/lever/postings-api"""

    platform = "lever"
    source_type = "ATS_LEVER"
    _BASE = "https://api.lever.co/v0/postings"

    def fetch_jobs(self) -> list[RawJobPosting]:
        data = self._get(f"{self._BASE}/{self.slug}", params={"mode": "json"})
        postings = []
        for job in data:
            categories = job.get("categories") or {}
            locations = [categories.get("location"), *(categories.get("allLocations") or [])]
            if not (job.get("country") == "JP" or is_japan_location(*locations)):
                continue
            sections = [job.get("descriptionPlain") or html_to_text(job.get("description"))]
            for block in job.get("lists") or []:
                sections.append(f"{block.get('text', '').strip()}\n{html_to_text(block.get('content'))}")
            sections.append(job.get("additionalPlain") or html_to_text(job.get("additional")))
            salary = job.get("salaryRange") or {}
            yearly = (salary.get("interval") or "").lower().startswith("per-year")
            postings.append(
                self._posting(
                    title=job["text"].strip(),
                    description="\n\n".join(s.strip() for s in sections if s and s.strip()),
                    source_job_id=job["id"],
                    source_url=job["hostedUrl"],
                    canonical_url=job["hostedUrl"],
                    location=categories.get("location"),
                    employment_type=infer_employment_type(categories.get("commitment"), job["text"]),
                    work_mode=infer_work_mode(job.get("workplaceType")),
                    salary_min=salary.get("min") if yearly else None,
                    salary_max=salary.get("max") if yearly else None,
                    salary_currency=salary.get("currency") if yearly else None,
                )
            )
        return postings

    def check_status(self, source_job_id: str) -> JobStatus:
        return self._status_from_url(f"{self._BASE}/{self.slug}/{source_job_id}")


class AshbySource(ATSJobSource):
    """https://developers.ashbyhq.com/docs/public-job-posting-api"""

    platform = "ashby"
    source_type = "ATS_ASHBY"
    _BASE = "https://api.ashbyhq.com/posting-api/job-board"

    def _board(self) -> list[dict]:
        data = self._get(f"{self._BASE}/{self.slug}", params={"includeCompensation": "true"})
        return [job for job in data.get("jobs", []) if job.get("isListed", True)]

    @staticmethod
    def _yearly_salary(job: dict) -> tuple[int | None, int | None, str | None]:
        for component in (job.get("compensation") or {}).get("summaryComponents") or []:
            if component.get("compensationType") == "Salary" and component.get("interval") == "1 YEAR":
                return component.get("minValue"), component.get("maxValue"), component.get("currencyCode")
        return None, None, None

    def fetch_jobs(self) -> list[RawJobPosting]:
        postings = []
        for job in self._board():
            secondary = job.get("secondaryLocations") or []
            countries = [((job.get("address") or {}).get("postalAddress") or {}).get("addressCountry")]
            countries += [((s.get("address") or {}).get("postalAddress") or {}).get("addressCountry") for s in secondary]
            if not is_japan_location(job.get("location"), *(s.get("location") for s in secondary), *countries):
                continue
            salary_min, salary_max, currency = self._yearly_salary(job)
            postings.append(
                self._posting(
                    title=job["title"].strip(),
                    description=job.get("descriptionPlain") or html_to_text(job.get("descriptionHtml")),
                    source_job_id=job["id"],
                    source_url=job["jobUrl"],
                    canonical_url=job["jobUrl"],
                    location=job.get("location"),
                    employment_type=infer_employment_type(job.get("employmentType"), job["title"]),
                    work_mode=infer_work_mode(job.get("workplaceType")),
                    salary_min=int(salary_min) if salary_min else None,
                    salary_max=int(salary_max) if salary_max else None,
                    salary_currency=currency,
                )
            )
        return postings

    def check_status(self, source_job_id: str) -> JobStatus:
        # Ashby has no per-posting endpoint; the board listing is the source of truth.
        try:
            listed = {job["id"] for job in self._board()}
        except httpx.HTTPError:
            return JobStatus.UNKNOWN
        return JobStatus.ACTIVE if source_job_id in listed else JobStatus.CLOSED


class SmartRecruitersSource(ATSJobSource):
    """https://developers.smartrecruiters.com/docs/posting-api"""

    platform = "smartrecruiters"
    source_type = "ATS_SMARTRECRUITERS"
    _BASE = "https://api.smartrecruiters.com/v1/companies"
    _PAGE_SIZE = 100
    # Listings omit descriptions, so each posting costs one extra request;
    # cap per board to keep a run polite and quick.
    _MAX_POSTINGS = 200

    def fetch_jobs(self) -> list[RawJobPosting]:
        summaries: list[dict] = []
        offset = 0
        while len(summaries) < self._MAX_POSTINGS:
            page = self._get(
                f"{self._BASE}/{self.slug}/postings",
                params={"country": "jp", "limit": self._PAGE_SIZE, "offset": offset},
            )
            content = page.get("content") or []
            summaries.extend(content)
            offset += len(content)
            if not content or offset >= page.get("totalFound", 0):
                break

        postings = []
        for summary in summaries[: self._MAX_POSTINGS]:
            try:
                detail = self._get(f"{self._BASE}/{self.slug}/postings/{summary['id']}")
            except httpx.HTTPError:
                logger.warning("Skipping SmartRecruiters posting %s: detail fetch failed", summary.get("id"))
                continue
            sections = (detail.get("jobAd") or {}).get("sections") or {}
            description = "\n\n".join(
                f"{section.get('title', '')}\n{html_to_text(section.get('text'))}".strip()
                for key in ("jobDescription", "qualifications", "additionalInformation", "companyDescription")
                if (section := sections.get(key)) and section.get("text")
            )
            location = detail.get("location") or {}
            city = ", ".join(v for v in (location.get("city"), "Japan") if v)
            mode = "remote" if location.get("remote") else "hybrid" if location.get("hybrid") else "onsite"
            postings.append(
                self._posting(
                    title=detail["name"].strip(),
                    description=description,
                    source_job_id=str(detail["id"]),
                    source_url=detail["postingUrl"],
                    canonical_url=detail["postingUrl"],
                    location=city,
                    employment_type=infer_employment_type(
                        (detail.get("typeOfEmployment") or {}).get("label"), detail["name"]
                    ),
                    work_mode=infer_work_mode(mode),
                )
            )
        return postings

    def check_status(self, source_job_id: str) -> JobStatus:
        try:
            detail = self._get(f"{self._BASE}/{self.slug}/postings/{source_job_id}")
        except httpx.HTTPStatusError as exc:
            return JobStatus.CLOSED if exc.response.status_code == 404 else JobStatus.UNKNOWN
        except httpx.HTTPError:
            return JobStatus.UNKNOWN
        return JobStatus.ACTIVE if detail.get("active", True) else JobStatus.CLOSED


PLATFORMS: dict[str, type[ATSJobSource]] = {
    cls.platform: cls for cls in (GreenhouseSource, LeverSource, AshbySource, SmartRecruitersSource)
}
