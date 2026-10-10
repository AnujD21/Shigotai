from app.ingestion.base import JobSourceAdapter, RawJobPosting
from app.ingestion.pipeline import ingest_source
from app.models.enums import EmploymentType, JobStatus, WorkMode
from app.models.job import Job


class _FakeAdapter(JobSourceAdapter):
    source_type = "TEST"

    def __init__(self, postings, source_name="Fake Source"):
        self._postings = postings
        self.source_name = source_name

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
    adapter_a = _FakeAdapter([_posting(source_job_id="career-page-99")], source_name="Acme careers page")
    adapter_b = _FakeAdapter([_posting(source_job_id="greenhouse-abc")], source_name="greenhouse:acme")

    ingest_source(db_session, adapter_a)
    ingest_source(db_session, adapter_b)

    assert db_session.query(Job).filter(Job.title == "Backend Engineer").count() == 1


def test_same_title_twice_on_one_board_stays_two_jobs(db_session):
    """Boards list separate openings with identical titles ("Account
    Executive" x2 in Tokyo); within one source the posting id decides."""
    adapter = _FakeAdapter([_posting(source_job_id="ae-1"), _posting(source_job_id="ae-2")])

    ingest_source(db_session, adapter)
    ingest_source(db_session, adapter)

    assert db_session.query(Job).count() == 2


def test_posting_removed_from_board_is_closed(db_session):
    ingest_source(db_session, _FakeAdapter([_posting(source_job_id="a"), _posting(source_job_id="b", title="SRE")]))

    ingest_source(db_session, _FakeAdapter([_posting(source_job_id="a")]), close_missing=True)

    statuses = {job.source_job_id: job.status for job in db_session.query(Job).all()}
    assert statuses == {"a": JobStatus.ACTIVE, "b": JobStatus.CLOSED}


def test_failed_fetch_closes_nothing(db_session):
    ingest_source(db_session, _FakeAdapter([_posting()]))

    class _DownAdapter(_FakeAdapter):
        def fetch_jobs(self):
            raise ConnectionError("board unreachable")

    try:
        ingest_source(db_session, _DownAdapter([]), close_missing=True)
    except ConnectionError:
        pass

    assert db_session.query(Job).one().status == JobStatus.ACTIVE


def test_different_locations_are_not_merged(db_session):
    adapter_a = _FakeAdapter([_posting(source_job_id="a", location="Tokyo")])
    adapter_b = _FakeAdapter([_posting(source_job_id="b", location="Osaka")])

    ingest_source(db_session, adapter_a)
    ingest_source(db_session, adapter_b)

    assert db_session.query(Job).count() == 2
