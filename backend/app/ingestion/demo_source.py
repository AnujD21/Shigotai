"""Clearly-labeled demo dataset so Shigotai is fully runnable without a live
job API integration (master spec section 48). Every job produced here is
flagged is_demo_data=True end-to-end and the UI must never present it as a
real, currently-hiring posting.
"""

from app.ingestion.base import JobSourceAdapter, RawJobPosting
from app.models.enums import EmploymentType, JobStatus, WorkMode

_JOBS: list[RawJobPosting] = [
    RawJobPosting(
        company_name="Kaede Robotics",
        company_website="https://kaede-robotics.example.jp",
        title="Computer Vision Engineer",
        description=(
            "Kaede Robotics builds warehouse automation robots deployed across Japan. "
            "We are looking for a Computer Vision Engineer to improve our object detection and tracking stack.\n\n"
            "Required: Python, PyTorch, OpenCV, YOLO, object detection, Docker. Bachelor's degree in Computer Science "
            "or a related field. 2+ years of experience building computer vision systems. "
            "日本語能力N2以上 (Business-level Japanese communication required for daily standups with the hardware team).\n\n"
            "Preferred: AWS, ONNX, Kubernetes.\n\n"
            "Visa sponsorship available for qualified candidates. New graduates are not eligible for this role -- "
            "we're looking for experienced candidates only."
        ),
        description_language="mixed",
        source_job_id="kaede-cv-2091",
        source_url="https://kaede-robotics.example.jp/careers/2091",
        canonical_url="https://kaede-robotics.example.jp/careers/2091",
        location="Yokohama, Kanagawa",
        employment_type=EmploymentType.FULL_TIME,
        work_mode=WorkMode.HYBRID,
        salary_min=6500000,
        salary_max=9500000,
        salary_currency="JPY",
        industry="Robotics",
    ),
    RawJobPosting(
        company_name="Hikari Systems",
        company_website="https://hikari-systems.example.jp",
        title="AI Engineer, New Graduate",
        description=(
            "Hikari Systems is hiring new graduate AI Engineers for our Tokyo research team. "
            "You'll work on applied machine learning for retail demand forecasting.\n\n"
            "Required: Python, TensorFlow or PyTorch, machine learning fundamentals. Bachelor's degree. "
            "New graduates are welcome to apply -- this is an entry-level position, no prior full-time experience required.\n\n"
            "Preferred: scikit-learn, SQL, AWS.\n\n"
            "日本語能力N3以上 (JLPT N3 or above; ability to read technical documentation in Japanese). "
            "Business-level English required for cross-team documentation.\n\n"
            "Visa sponsorship available -- we regularly sponsor work visas for international new graduates."
        ),
        description_language="mixed",
        source_job_id="hikari-newgrad-ai-14",
        source_url="https://hikari-systems.example.jp/careers/14",
        canonical_url="https://hikari-systems.example.jp/careers/14",
        location="Tokyo (Shibuya)",
        employment_type=EmploymentType.NEW_GRADUATE,
        work_mode=WorkMode.HYBRID,
        salary_min=4800000,
        salary_max=5800000,
        salary_currency="JPY",
        industry="Retail Technology",
    ),
    RawJobPosting(
        company_name="Sumire Analytics",
        company_website="https://sumire-analytics.example.jp",
        title="Machine Learning Engineer",
        description=(
            "Sumire Analytics builds fraud-detection systems for regional banks across Japan.\n\n"
            "Required: Python, scikit-learn, SQL, machine learning, 3+ years of experience. Master's degree preferred but "
            "not mandatory with sufficient industry experience.\n\n"
            "Preferred: PyTorch, Docker, AWS, natural language processing.\n\n"
            "日本語能力N2以上 required -- you will present findings directly to bank compliance teams in Japanese.\n\n"
            "Visa sponsorship is not available for this role; candidates must already hold a valid Japanese work visa."
        ),
        description_language="mixed",
        source_job_id="sumire-mle-77",
        source_url="https://sumire-analytics.example.jp/jobs/77",
        canonical_url="https://sumire-analytics.example.jp/jobs/77",
        location="Osaka",
        employment_type=EmploymentType.FULL_TIME,
        work_mode=WorkMode.ONSITE,
        salary_min=7500000,
        salary_max=10500000,
        salary_currency="JPY",
        industry="Financial Technology",
    ),
    RawJobPosting(
        company_name="Nagomi Cloud",
        company_website="https://nagomi-cloud.example.jp",
        title="Backend Engineer (Python)",
        description=(
            "Nagomi Cloud provides SaaS infrastructure tooling for mid-size Japanese enterprises.\n\n"
            "Required: Python, FastAPI or Django, SQL, Docker, Git, 1+ years of experience.\n\n"
            "Preferred: AWS, Kubernetes, CI/CD, TypeScript.\n\n"
            "Japanese: business-level Japanese communication required for team meetings and documentation.\n\n"
            "New graduates are welcome to apply if they have strong internship experience. "
            "Visa sponsorship available."
        ),
        description_language="en",
        source_job_id="nagomi-be-203",
        source_url="https://nagomi-cloud.example.jp/careers/203",
        canonical_url="https://nagomi-cloud.example.jp/careers/203",
        location="Tokyo (Remote within Japan)",
        employment_type=EmploymentType.FULL_TIME,
        work_mode=WorkMode.REMOTE,
        salary_min=5500000,
        salary_max=8000000,
        salary_currency="JPY",
        industry="Enterprise SaaS",
    ),
    RawJobPosting(
        company_name="Tsubaki FinTech",
        company_website="https://tsubaki-fintech.example.jp",
        title="Frontend Engineer (React)",
        description=(
            "Tsubaki FinTech is building the next generation of consumer investing apps in Japan.\n\n"
            "Required: JavaScript, TypeScript, React, Next.js, Git, 2+ years of experience.\n\n"
            "Preferred: Node.js, Figma collaboration experience.\n\n"
            "日本語能力N3以上 (JLPT N3 or above). English also used daily with our Singapore design team.\n\n"
            "Visa sponsorship: not stated in this posting."
        ),
        description_language="mixed",
        source_job_id="tsubaki-fe-58",
        source_url="https://tsubaki-fintech.example.jp/jobs/58",
        canonical_url="https://tsubaki-fintech.example.jp/jobs/58",
        location="Tokyo (Minato)",
        employment_type=EmploymentType.FULL_TIME,
        work_mode=WorkMode.HYBRID,
        salary_min=6000000,
        salary_max=8500000,
        salary_currency="JPY",
        industry="Financial Technology",
    ),
    RawJobPosting(
        company_name="Orient Vision Labs",
        company_website="https://orient-vision.example.jp",
        title="Drone Perception Software Engineer",
        description=(
            "Orient Vision Labs develops perception software for agricultural drones operating across rural Japan.\n\n"
            "Required: computer vision, object detection, YOLO, OpenCV, PyTorch, Python, 1+ years of experience "
            "(internship experience considered). Bachelor's degree in Computer Science, Robotics, or related field.\n\n"
            "Preferred: ONNX, embedded systems, drone or robotics project experience.\n\n"
            "Japanese: business-level Japanese communication required. JLPT not specifically required if business "
            "Japanese ability can be demonstrated.\n\n"
            "New graduates welcome. Visa sponsorship available for the right candidate."
        ),
        description_language="en",
        source_job_id="orient-drone-9",
        source_url="https://orient-vision.example.jp/careers/9",
        canonical_url="https://orient-vision.example.jp/careers/9",
        location="Sapporo, Hokkaido",
        employment_type=EmploymentType.FULL_TIME,
        work_mode=WorkMode.ONSITE,
        salary_min=5200000,
        salary_max=7200000,
        salary_currency="JPY",
        industry="Agricultural Technology",
    ),
    RawJobPosting(
        company_name="Enokida AI",
        company_website="https://enokida-ai.example.jp",
        title="NLP Engineer",
        description=(
            "Enokida AI builds Japanese-language customer support automation for e-commerce companies.\n\n"
            "Required: Python, natural language processing, PyTorch or TensorFlow, 2+ years of experience. "
            "Master's degree in Computer Science, Computational Linguistics, or related field preferred.\n\n"
            "Preferred: large language models, LLM fine-tuning, transformers.\n\n"
            "日本語能力N1 required -- you'll be reviewing native-level customer support transcripts daily.\n\n"
            "Visa sponsorship available."
        ),
        description_language="mixed",
        source_job_id="enokida-nlp-31",
        source_url="https://enokida-ai.example.jp/jobs/31",
        canonical_url="https://enokida-ai.example.jp/jobs/31",
        location="Fukuoka",
        employment_type=EmploymentType.FULL_TIME,
        work_mode=WorkMode.HYBRID,
        salary_min=7000000,
        salary_max=9800000,
        salary_currency="JPY",
        industry="E-commerce",
    ),
    RawJobPosting(
        company_name="Shirakawa Mobility",
        company_website="https://shirakawa-mobility.example.jp",
        title="DevOps Engineer",
        description=(
            "Shirakawa Mobility operates EV charging network software across Japan.\n\n"
            "Required: Docker, Kubernetes, AWS, CI/CD, Linux, 3+ years of experience.\n\n"
            "Preferred: Terraform, Python, Go.\n\n"
            "Business-level Japanese communication required for on-call coordination with the Tokyo infrastructure team.\n\n"
            "Visa sponsorship is not available for this role."
        ),
        description_language="en",
        source_job_id="shirakawa-devops-45",
        source_url="https://shirakawa-mobility.example.jp/careers/45",
        canonical_url="https://shirakawa-mobility.example.jp/careers/45",
        location="Nagoya, Aichi",
        employment_type=EmploymentType.FULL_TIME,
        work_mode=WorkMode.ONSITE,
        salary_min=7200000,
        salary_max=10000000,
        salary_currency="JPY",
        industry="Mobility / EV Infrastructure",
    ),
    RawJobPosting(
        company_name="Kotobuki Games",
        company_website="https://kotobuki-games.example.jp",
        title="Gameplay Software Engineer (New Graduate)",
        description=(
            "Kotobuki Games is hiring new graduate engineers for our Tokyo mobile games studio.\n\n"
            "Required: C++ or C#, Git, computer science fundamentals. New graduates welcome -- no professional "
            "experience required, internship or personal projects are enough.\n\n"
            "Preferred: Unity, mobile development experience.\n\n"
            "日本語能力N2以上 required for daily design reviews.\n\n"
            "Visa sponsorship available for new graduates joining from overseas universities."
        ),
        description_language="mixed",
        source_job_id="kotobuki-gp-12",
        source_url="https://kotobuki-games.example.jp/careers/12",
        canonical_url="https://kotobuki-games.example.jp/careers/12",
        location="Tokyo (Shinjuku)",
        employment_type=EmploymentType.NEW_GRADUATE,
        work_mode=WorkMode.ONSITE,
        salary_min=4500000,
        salary_max=5200000,
        salary_currency="JPY",
        industry="Gaming",
    ),
    RawJobPosting(
        company_name="Aozora Data",
        company_website="https://aozora-data.example.jp",
        title="Data Scientist",
        description=(
            "Aozora Data works with logistics companies to optimize delivery routes nationwide.\n\n"
            "Required: Python, SQL, scikit-learn, statistics, 2+ years of experience.\n\n"
            "Preferred: PyTorch, AWS, Docker.\n\n"
            "日本語能力N3以上 (JLPT N3 or above) required. English used for internal tooling documentation.\n\n"
            "Visa sponsorship available."
        ),
        description_language="mixed",
        source_job_id="aozora-ds-88",
        source_url="https://aozora-data.example.jp/jobs/88",
        canonical_url="https://aozora-data.example.jp/jobs/88",
        location="Tokyo (Remote within Japan)",
        employment_type=EmploymentType.FULL_TIME,
        work_mode=WorkMode.REMOTE,
        salary_min=6200000,
        salary_max=8800000,
        salary_currency="JPY",
        industry="Logistics Technology",
    ),
    RawJobPosting(
        company_name="Meikei Semiconductor",
        company_website="https://meikei-semi.example.jp",
        title="Embedded Software Engineer",
        description=(
            "Meikei Semiconductor designs edge-AI chips for industrial sensors.\n\n"
            "Required: C++, embedded Linux, Git, 3+ years of experience. Bachelor's degree in Electrical Engineering, "
            "Computer Engineering, or Computer Science.\n\n"
            "Preferred: ONNX, TensorFlow Lite, hardware-software co-design experience.\n\n"
            "Japanese: business-level Japanese communication required for coordination with the fabrication team in Kyoto.\n\n"
            "Visa sponsorship not stated in this posting."
        ),
        description_language="en",
        source_job_id="meikei-embedded-19",
        source_url="https://meikei-semi.example.jp/careers/19",
        canonical_url="https://meikei-semi.example.jp/careers/19",
        location="Kyoto",
        employment_type=EmploymentType.FULL_TIME,
        work_mode=WorkMode.ONSITE,
        salary_min=6800000,
        salary_max=9200000,
        salary_currency="JPY",
        industry="Semiconductors",
    ),
    RawJobPosting(
        company_name="Chiyoda Digital Bank",
        company_website="https://chiyoda-digital.example.jp",
        title="Site Reliability Engineer",
        description=(
            "Chiyoda Digital Bank runs core banking infrastructure for one of Japan's largest digital-first banks.\n\n"
            "Required: Kubernetes, AWS, Python or Go, CI/CD, 4+ years of experience.\n\n"
            "Preferred: Terraform, observability tooling, financial services background.\n\n"
            "日本語能力N2以上 required -- regulatory documentation and incident reports must be written in Japanese.\n\n"
            "Visa sponsorship is not available; a valid work visa in Japan is required at time of application."
        ),
        description_language="mixed",
        source_job_id="chiyoda-sre-6",
        source_url="https://chiyoda-digital.example.jp/careers/6",
        canonical_url="https://chiyoda-digital.example.jp/careers/6",
        location="Tokyo (Chiyoda)",
        employment_type=EmploymentType.FULL_TIME,
        work_mode=WorkMode.HYBRID,
        salary_min=8500000,
        salary_max=12000000,
        salary_currency="JPY",
        industry="Digital Banking",
    ),
    RawJobPosting(
        company_name="Fujimori Robotics",
        company_website="https://fujimori-robotics.example.jp",
        title="Robotics Software Intern",
        description=(
            "Fujimori Robotics is offering a 6-month internship on our humanoid robotics perception team.\n\n"
            "Required: Python, ROS or similar robotics framework familiarity, computer vision coursework or projects.\n\n"
            "Preferred: OpenCV, PyTorch, drone or robotics competition experience.\n\n"
            "日本語能力N4以上 (basic Japanese sufficient; team communicates primarily in English with Japanese "
            "documentation support).\n\n"
            "This internship is open to current students and recent graduates. Visa sponsorship available for "
            "eligible internship visas."
        ),
        description_language="mixed",
        source_job_id="fujimori-intern-3",
        source_url="https://fujimori-robotics.example.jp/careers/3",
        canonical_url="https://fujimori-robotics.example.jp/careers/3",
        location="Tsukuba, Ibaraki",
        employment_type=EmploymentType.INTERNSHIP,
        work_mode=WorkMode.ONSITE,
        salary_min=None,
        salary_max=None,
        salary_currency="JPY",
        industry="Robotics",
    ),
    RawJobPosting(
        company_name="Ranatech K.K.",
        company_website="https://ranatech.example.jp",
        title="Full-Stack Engineer",
        description=(
            "Ranatech K.K. builds HR software used by mid-size Japanese manufacturers.\n\n"
            "Required: TypeScript, React, Node.js, SQL, 2+ years of experience.\n\n"
            "Preferred: Next.js, Docker, AWS.\n\n"
            "日本語能力N2以上 required for client-facing implementation calls.\n\n"
            "New graduates are not eligible for this role. Visa sponsorship available."
        ),
        description_language="mixed",
        source_job_id="ranatech-fs-64",
        source_url="https://ranatech.example.jp/jobs/64",
        canonical_url="https://ranatech.example.jp/jobs/64",
        location="Tokyo (Shinagawa)",
        employment_type=EmploymentType.FULL_TIME,
        work_mode=WorkMode.HYBRID,
        salary_min=6500000,
        salary_max=9000000,
        salary_currency="JPY",
        industry="HR Technology",
    ),
    RawJobPosting(
        company_name="Sanko Freight Systems",
        company_website="https://sanko-freight.example.jp",
        title="Software Engineer (New Graduate)",
        description=(
            "Sanko Freight Systems modernizes freight-tracking software for Japan's shipping industry.\n\n"
            "Required: Java or Python, SQL, Git. New graduates welcome -- entry-level position, training provided.\n\n"
            "Preferred: Spring Boot, AWS.\n\n"
            "日本語能力N3以上 (JLPT N3 or above) required for onboarding training conducted in Japanese.\n\n"
            "Visa sponsorship available for new graduate hires."
        ),
        description_language="mixed",
        source_job_id="sanko-newgrad-22",
        source_url="https://sanko-freight.example.jp/careers/22",
        canonical_url="https://sanko-freight.example.jp/careers/22",
        location="Kobe, Hyogo",
        employment_type=EmploymentType.NEW_GRADUATE,
        work_mode=WorkMode.ONSITE,
        salary_min=4600000,
        salary_max=5400000,
        salary_currency="JPY",
        industry="Logistics",
    ),
]


class DemoJobSource(JobSourceAdapter):
    source_name = "Shigotai Demo Dataset"
    source_type = "DEMO"

    def fetch_jobs(self) -> list[RawJobPosting]:
        return list(_JOBS)

    def check_status(self, source_job_id: str) -> JobStatus:
        # Demo postings are treated as consistently active; a real adapter
        # would re-fetch the source page/API here.
        return JobStatus.ACTIVE
