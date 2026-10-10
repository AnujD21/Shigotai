"""ATS adapters parsed against payloads shaped like the real APIs' responses
(captured Oct 2026), with the HTTP layer stubbed out."""

from app.ingestion.ats_sources import AshbySource, GreenhouseSource, LeverSource, SmartRecruitersSource
from app.ingestion.text import detect_language, html_to_text
from app.models.enums import EmploymentType, WorkMode


def _stub(adapter, responses):
    adapter._get = lambda url, params=None: responses[url]
    return adapter


def test_greenhouse_keeps_only_japan_roles_and_decodes_html():
    adapter = _stub(
        GreenhouseSource("acme", "Acme"),
        {
            "https://boards-api.greenhouse.io/v1/boards/acme/jobs": {
                "jobs": [
                    {
                        "id": 501,
                        "title": "Applied AI Engineer",
                        "location": {"name": "Tokyo, Japan"},
                        "absolute_url": "https://job-boards.greenhouse.io/acme/jobs/501",
                        "content": "&lt;p&gt;Required: Python&lt;/p&gt;&lt;ul&gt;&lt;li&gt;Docker&lt;/li&gt;&lt;/ul&gt;",
                        "metadata": [{"name": "Location Type", "value": "On-Site"}],
                        "departments": [],
                        "offices": [],
                    },
                    {
                        "id": 502,
                        "title": "Account Executive",
                        "location": {"name": "London, UK"},
                        "absolute_url": "https://job-boards.greenhouse.io/acme/jobs/502",
                        "content": "",
                    },
                ]
            }
        },
    )

    postings = adapter.fetch_jobs()

    assert [p.source_job_id for p in postings] == ["501"]
    assert postings[0].description == "Required: Python\n\n- Docker"
    assert postings[0].work_mode == WorkMode.ONSITE
    assert postings[0].company_name == "Acme"


def test_greenhouse_uses_japan_office_when_location_is_a_work_mode():
    adapter = _stub(
        GreenhouseSource("cf", "Cloudflare"),
        {
            "https://boards-api.greenhouse.io/v1/boards/cf/jobs": {
                "jobs": [
                    {
                        "id": 9,
                        "title": "Network Security Engineer",
                        "location": {"name": "Hybrid"},
                        "offices": [{"name": "Tokyo, Japan", "location": "Tokyo, Japan"}],
                        "absolute_url": "https://boards.greenhouse.io/cf/jobs/9",
                        "content": "",
                    }
                ]
            }
        },
    )

    [posting] = adapter.fetch_jobs()

    assert posting.location == "Tokyo, Japan"
    assert posting.work_mode == WorkMode.HYBRID


def test_lever_reads_japanese_locations_and_commitment():
    adapter = _stub(
        LeverSource("woven", "Woven"),
        {
            "https://api.lever.co/v0/postings/woven": [
                {
                    "id": "abc",
                    "text": "AD/ADAS SIL環境開発エンジニア",
                    "categories": {"location": "東京都中央区", "commitment": "正社員", "allLocations": ["東京都中央区"]},
                    "workplaceType": "hybrid",
                    "hostedUrl": "https://jobs.lever.co/woven/abc",
                    "descriptionPlain": "自動運転のシミュレーション環境を開発します。",
                    "lists": [{"text": "必須スキル", "content": "<li>C++</li><li>Python</li>"}],
                    "additionalPlain": "",
                },
                {
                    "id": "def",
                    "text": "Summer Intern",
                    "categories": {"location": "Palo Alto", "commitment": "Intern"},
                    "hostedUrl": "https://jobs.lever.co/woven/def",
                },
            ]
        },
    )

    postings = adapter.fetch_jobs()

    assert len(postings) == 1
    assert postings[0].work_mode == WorkMode.HYBRID
    assert postings[0].employment_type == EmploymentType.FULL_TIME
    assert "必須スキル\n- C++\n- Python" in postings[0].description
    assert postings[0].description_language == "ja"


def test_ashby_uses_secondary_locations_and_yearly_salary():
    adapter = _stub(
        AshbySource("openai", "OpenAI"),
        {
            "https://api.ashbyhq.com/posting-api/job-board/openai": {
                "jobs": [
                    {
                        "id": "j1",
                        "title": "Forward Deployed Engineer",
                        "location": "San Francisco",
                        "secondaryLocations": [{"location": "Tokyo, Japan"}],
                        "employmentType": "FullTime",
                        "workplaceType": "Hybrid",
                        "jobUrl": "https://jobs.ashbyhq.com/openai/j1",
                        "descriptionPlain": "Build with customers.",
                        "isListed": True,
                        "compensation": {
                            "summaryComponents": [
                                {"compensationType": "Salary", "interval": "1 YEAR", "currencyCode": "JPY",
                                 "minValue": 12000000, "maxValue": 18000000}
                            ]
                        },
                    },
                    {"id": "j2", "title": "Unlisted", "location": "Tokyo", "isListed": False, "jobUrl": "x"},
                ]
            }
        },
    )

    postings = adapter.fetch_jobs()

    assert [p.source_job_id for p in postings] == ["j1"]
    assert (postings[0].salary_min, postings[0].salary_max, postings[0].salary_currency) == (12000000, 18000000, "JPY")


def test_smartrecruiters_fetches_detail_for_description():
    base = "https://api.smartrecruiters.com/v1/companies/Bosch/postings"
    adapter = _stub(
        SmartRecruitersSource("Bosch", "Bosch"),
        {
            base: {"totalFound": 1, "content": [{"id": "77"}]},
            f"{base}/77": {
                "id": "77",
                "name": "Internship at Vehicle Motion",
                "postingUrl": "https://jobs.smartrecruiters.com/Bosch/77",
                "location": {"city": "Yokohama", "hybrid": True},
                "typeOfEmployment": {"label": "Intern"},
                "jobAd": {"sections": {"jobDescription": {"title": "Job Description", "text": "<p>Analyze data.</p>"}}},
            },
        },
    )

    [posting] = adapter.fetch_jobs()

    assert posting.location == "Yokohama, Japan"
    assert posting.employment_type == EmploymentType.INTERNSHIP
    assert posting.work_mode == WorkMode.HYBRID
    assert posting.description == "Job Description\nAnalyze data."


def test_html_to_text_drops_scripts_and_collapses_whitespace():
    assert html_to_text("<div>Hello&nbsp; <b>world</b></div><script>x()</script><p></p><p>Bye</p>") == "Hello world\n\nBye"


def test_detect_language():
    assert detect_language("We are hiring a backend engineer in Tokyo.") == "en"
    assert detect_language("自動運転のシミュレーション環境を開発します。") == "ja"
    assert detect_language("We are hiring a backend engineer for our payments platform. 日本語能力N2以上") == "mixed"
