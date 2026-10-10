"""Curated skill taxonomy used for profile input suggestions and semantic
grouping in the matching engine. This intentionally favors a small, accurate
list over an exhaustive one: the matching engine never invents a relationship
that isn't encoded here.

Detection is boundary-aware (see `find_skills`): real job postings and
resumes are long free text, so naive substring checks produce false
positives -- "Go" inside "Google", "Java" inside "JavaScript", "Git" inside
"digital", "Vue" inside "revenue".
"""

import re
from functools import lru_cache

from app.models.enums import SkillCategory

SKILL_CATALOG: dict[str, SkillCategory] = {
    "Python": SkillCategory.PROGRAMMING_LANGUAGE,
    "Java": SkillCategory.PROGRAMMING_LANGUAGE,
    "JavaScript": SkillCategory.PROGRAMMING_LANGUAGE,
    "TypeScript": SkillCategory.PROGRAMMING_LANGUAGE,
    "C++": SkillCategory.PROGRAMMING_LANGUAGE,
    "C#": SkillCategory.PROGRAMMING_LANGUAGE,
    "Go": SkillCategory.PROGRAMMING_LANGUAGE,
    "Rust": SkillCategory.PROGRAMMING_LANGUAGE,
    "Kotlin": SkillCategory.PROGRAMMING_LANGUAGE,
    "Swift": SkillCategory.PROGRAMMING_LANGUAGE,
    "Ruby": SkillCategory.PROGRAMMING_LANGUAGE,
    "PHP": SkillCategory.PROGRAMMING_LANGUAGE,
    "Scala": SkillCategory.PROGRAMMING_LANGUAGE,
    "SQL": SkillCategory.PROGRAMMING_LANGUAGE,
    "React": SkillCategory.FRAMEWORK,
    "Next.js": SkillCategory.FRAMEWORK,
    "Vue": SkillCategory.FRAMEWORK,
    "Django": SkillCategory.FRAMEWORK,
    "FastAPI": SkillCategory.FRAMEWORK,
    "Flask": SkillCategory.FRAMEWORK,
    "Spring Boot": SkillCategory.FRAMEWORK,
    "Node.js": SkillCategory.FRAMEWORK,
    "Ruby on Rails": SkillCategory.FRAMEWORK,
    "GraphQL": SkillCategory.FRAMEWORK,
    "Flutter": SkillCategory.FRAMEWORK,
    "React Native": SkillCategory.FRAMEWORK,
    "Android": SkillCategory.FRAMEWORK,
    "iOS": SkillCategory.FRAMEWORK,
    "ROS": SkillCategory.FRAMEWORK,
    "TensorFlow": SkillCategory.AI_ML,
    "PyTorch": SkillCategory.AI_ML,
    "YOLO": SkillCategory.AI_ML,
    "OpenCV": SkillCategory.AI_ML,
    "ONNX": SkillCategory.AI_ML,
    "scikit-learn": SkillCategory.AI_ML,
    "Keras": SkillCategory.AI_ML,
    "CUDA": SkillCategory.AI_ML,
    "Computer Vision": SkillCategory.AI_ML,
    "Natural Language Processing": SkillCategory.AI_ML,
    "LLM": SkillCategory.AI_ML,
    "LLM Fine-tuning": SkillCategory.AI_ML,
    "Reinforcement Learning": SkillCategory.AI_ML,
    "MLOps": SkillCategory.AI_ML,
    "Pandas": SkillCategory.AI_ML,
    "Spark": SkillCategory.AI_ML,
    "Docker": SkillCategory.CLOUD_DEVOPS,
    "Kubernetes": SkillCategory.CLOUD_DEVOPS,
    "AWS": SkillCategory.CLOUD_DEVOPS,
    "GCP": SkillCategory.CLOUD_DEVOPS,
    "Azure": SkillCategory.CLOUD_DEVOPS,
    "Terraform": SkillCategory.CLOUD_DEVOPS,
    "CI/CD": SkillCategory.CLOUD_DEVOPS,
    "Kafka": SkillCategory.CLOUD_DEVOPS,
    "Airflow": SkillCategory.CLOUD_DEVOPS,
    "PostgreSQL": SkillCategory.TOOL,
    "MySQL": SkillCategory.TOOL,
    "MongoDB": SkillCategory.TOOL,
    "Redis": SkillCategory.TOOL,
    "Git": SkillCategory.TOOL,
    "Linux": SkillCategory.TOOL,
    "Figma": SkillCategory.TOOL,
    "Salesforce": SkillCategory.TOOL,
}

# Alternate spellings that should resolve to a catalog name. Matching and
# canonicalization are case-insensitive unless the skill is listed in
# _CASE_SENSITIVE below.
SKILL_ALIASES: dict[str, list[str]] = {
    "Go": ["Golang"],
    "JavaScript": ["JS", "ECMAScript"],
    "TypeScript": ["TS"],
    "C++": ["CPP"],
    "React": ["React.js", "ReactJS"],
    "Next.js": ["NextJS"],
    "Vue": ["Vue.js", "VueJS"],
    "Node.js": ["NodeJS"],
    "Ruby on Rails": ["Rails"],
    "scikit-learn": ["sklearn", "scikit learn"],
    "Natural Language Processing": ["NLP"],
    "LLM": ["LLMs", "large language models", "large language model"],
    "LLM Fine-tuning": ["LLM fine tuning", "fine-tuning LLMs", "fine-tuning large language models"],
    "Computer Vision": ["machine vision"],
    "Kubernetes": ["K8s"],
    "AWS": ["Amazon Web Services"],
    "GCP": ["Google Cloud", "Google Cloud Platform"],
    "Azure": ["Microsoft Azure"],
    "CI/CD": ["CICD", "continuous integration"],
    "PostgreSQL": ["Postgres"],
    "Spark": ["Apache Spark", "PySpark"],
    "Kafka": ["Apache Kafka"],
    "Airflow": ["Apache Airflow"],
}

# Skills whose names are also everyday English words. These only match with
# exact casing (and "Go" additionally never matches "go-to-market").
_CASE_SENSITIVE = {"Go", "Swift", "Ruby", "Spark", "Rust", "Flask", "Pandas", "ROS", "iOS", "JS", "TS", "Rails"}
# Two-letter aliases are too noisy for free-text detection (e.g. "TS" in a
# ticket number); they still canonicalize when a user types them explicitly.
_DETECTION_EXCLUDED_ALIASES = {"JS", "TS", "CPP"}

# Groups of interchangeable / closely related skills. Used by the semantic
# matching stage so that, e.g., a job asking for "computer vision experience"
# recognizes a candidate's YOLO/OpenCV/PyTorch background even though none of
# those exact tokens appear in the job text.
SEMANTIC_SKILL_GROUPS: list[set[str]] = [
    {"computer vision", "yolo", "opencv", "object detection", "image classification", "onnx", "image processing"},
    {"pytorch", "tensorflow", "keras", "deep learning", "neural networks", "machine learning"},
    {"nlp", "natural language processing", "llm", "large language models", "transformers", "llm fine-tuning"},
    {"react", "next.js", "frontend", "vue", "javascript", "typescript"},
    {"aws", "gcp", "azure", "cloud infrastructure", "cloud computing", "cloud platform"},
    {"docker", "kubernetes", "containerization", "devops", "ci/cd"},
    {"backend", "django", "fastapi", "flask", "spring boot", "node.js", "api development"},
    {"sql", "postgresql", "mysql", "database", "data modeling"},
    {"android", "ios", "flutter", "react native", "kotlin", "swift", "mobile"},
    {"spark", "kafka", "airflow", "data pipeline", "data engineering", "etl"},
]

_WORD_CHARS = r"A-Za-z0-9_"


def term_pattern(term: str, case_sensitive: bool = False) -> re.Pattern[str]:
    """Regex for `term` as a standalone token.

    Neighbouring letters/digits (and the +/# that make C++ and C# distinct)
    block a match, but CJK text does not -- "Go言語" and "Python経験" still
    count, since Japanese doesn't separate words with spaces.
    """
    body = re.escape(term)
    lookbehind = rf"(?<![{_WORD_CHARS}+#.])"
    lookahead = rf"(?![{_WORD_CHARS}+#])"
    if term == "Go":
        # The language vs. the verb: "Go To Market", "Go-live", "Go/No-Go",
        # "Go onsite" are all common in postings. "Python/Go" still matches.
        lookbehind += r"(?<!-)"
        lookahead += r"(?!-)(?!/No)(?!\s+(?i:to|onsite|on-site|beyond|above|ahead|back|live|out|deep|further|through)\b)"
    flags = 0 if case_sensitive else re.IGNORECASE
    return re.compile(rf"{lookbehind}{body}{lookahead}", flags)


@lru_cache
def _detection_patterns() -> list[tuple[str, list[re.Pattern[str]]]]:
    patterns = []
    for skill in SKILL_CATALOG:
        terms = [skill] + [a for a in SKILL_ALIASES.get(skill, []) if a not in _DETECTION_EXCLUDED_ALIASES]
        patterns.append(
            (skill, [term_pattern(t, case_sensitive=t in _CASE_SENSITIVE) for t in terms])
        )
    return patterns


def find_skills(text: str) -> list[str]:
    """Catalog skills mentioned in free text, in catalog order."""
    return [skill for skill, patterns in _detection_patterns() if any(p.search(text) for p in patterns)]


@lru_cache
def _canonical_lookup() -> dict[str, str]:
    lookup = {name.lower(): name for name in SKILL_CATALOG}
    for canonical, aliases in SKILL_ALIASES.items():
        for alias in aliases:
            lookup.setdefault(alias.lower(), canonical)
    return lookup


def canonical_skill_name(name: str) -> str:
    """Resolve casing/aliases to the catalog name ("pytorch" -> "PyTorch",
    "Golang" -> "Go"); unknown skills pass through trimmed."""
    stripped = name.strip()
    return _canonical_lookup().get(stripped.lower(), stripped)


def skill_key(name: str) -> str:
    """Comparison key so "K8s" on a profile matches "Kubernetes" in a job."""
    return canonical_skill_name(name).lower()


def infer_category(name: str) -> SkillCategory:
    return SKILL_CATALOG.get(canonical_skill_name(name), SkillCategory.OTHER)


def is_ai_ml_skill(name: str) -> bool:
    return infer_category(name) == SkillCategory.AI_ML
