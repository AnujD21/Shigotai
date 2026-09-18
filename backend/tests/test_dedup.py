from app.ingestion.base import JobSourceAdapter, RawJobPosting
from app.ingestion.pipeline import ingest_source
from app.models.enums import EmploymentType, JobStatus, WorkMode
from app.models.job import Job


class _FakeAdapter(JobSourceAdapter):
    source_name = "Fake Source"
    source_type = "TEST"

    def __init__(self, postings):
        self._postings = postings

    def fetch_jobs(self):
        return self._postings

    def check_status(self, source_job_id):
        return JobStatus.ACTIVE


def _posting(**overrides):
    defaults = dict(
        company_name="Acme K.K.",
        company_website="https://acme.example.jp",
        title="Backend Engineer",
        description="Python required.",
        description_language="en",
        source_job_id="job-1",
        source_url="https://acme.example.jp/jobs/1",
        canonical_url="https://acme.example.jp/jobs/1",
        location="Tokyo",
        employment_type=EmploymentType.FULL_TIME,
        work_mode=WorkMode.HYBRID,
    )
    defaults.update(overrides)
    return RawJobPosting(**defaults)


def test_reingesting_same_source_job_id_does_not_duplicate(db_session):
    adapter = _FakeAdapter([_posting()])
    ingest_source(db_session, adapter)
    ingest_source(db_session, adapter)

    assert db_session.query(Job).count() == 1


def test_changed_description_updates_existing_job_and_refreshes_hash(db_session):
    adapter = _FakeAdapter([_posting(description="Python required.")])
    ingest_source(db_session, adapter)
    original_hash = db_session.query(Job).one().content_hash

    adapter_v2 = _FakeAdapter([_posting(description="Python and Go required.")])
    ingest_source(db_session, adapter_v2)

    job = db_session.query(Job).one()
    assert job.content_hash != original_hash
    assert "Go" in job.original_description


def test_same_company_and_title_across_sources_deduplicates(db_session):
    """A posting seen via a company career page and again via an ATS feed
    (different source_job_id, no canonical id overlap) should still collapse
    into one job -- master spec section 10."""
    adapter_a = _FakeAdapter([_posting(source_job_id="career-page-99")])
    adapter_b = _FakeAdapter([_posting(source_job_id="greenhouse-abc")])

    ingest_source(db_session, adapter_a)
    ingest_source(db_session, adapter_b)

    assert db_session.query(Job).filter(Job.title == "Backend Engineer").count() == 1


def test_different_locations_are_not_merged(db_session):
    adapter_a = _FakeAdapter([_posting(source_job_id="a", location="Tokyo")])
    adapter_b = _FakeAdapter([_posting(source_job_id="b", location="Osaka")])

    ingest_source(db_session, adapter_a)
    ingest_source(db_session, adapter_b)

    assert db_session.query(Job).count() == 2
