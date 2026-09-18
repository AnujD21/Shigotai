"""Curated skill taxonomy used for profile input suggestions and semantic
grouping in the matching engine. This intentionally favors a small, accurate
list over an exhaustive one: the matching engine never invents a relationship
that isn't encoded here.
"""

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
    "SQL": SkillCategory.PROGRAMMING_LANGUAGE,
    "React": SkillCategory.FRAMEWORK,
    "Next.js": SkillCategory.FRAMEWORK,
    "Vue": SkillCategory.FRAMEWORK,
    "Django": SkillCategory.FRAMEWORK,
    "FastAPI": SkillCategory.FRAMEWORK,
    "Flask": SkillCategory.FRAMEWORK,
    "Spring Boot": SkillCategory.FRAMEWORK,
    "Node.js": SkillCategory.FRAMEWORK,
    "TensorFlow": SkillCategory.AI_ML,
    "PyTorch": SkillCategory.AI_ML,
    "YOLO": SkillCategory.AI_ML,
    "OpenCV": SkillCategory.AI_ML,
    "ONNX": SkillCategory.AI_ML,
    "scikit-learn": SkillCategory.AI_ML,
    "Keras": SkillCategory.AI_ML,
    "Computer Vision": SkillCategory.AI_ML,
    "Natural Language Processing": SkillCategory.AI_ML,
    "LLM Fine-tuning": SkillCategory.AI_ML,
    "Reinforcement Learning": SkillCategory.AI_ML,
    "Docker": SkillCategory.CLOUD_DEVOPS,
    "Kubernetes": SkillCategory.CLOUD_DEVOPS,
    "AWS": SkillCategory.CLOUD_DEVOPS,
    "GCP": SkillCategory.CLOUD_DEVOPS,
    "Azure": SkillCategory.CLOUD_DEVOPS,
    "Terraform": SkillCategory.CLOUD_DEVOPS,
    "CI/CD": SkillCategory.CLOUD_DEVOPS,
    "Git": SkillCategory.TOOL,
    "Linux": SkillCategory.TOOL,
    "Figma": SkillCategory.TOOL,
}

# Groups of interchangeable / closely related skills. Used by the semantic
# matching stage so that, e.g., a job asking for "computer vision experience"
# recognizes a candidate's YOLO/OpenCV/PyTorch background even though none of
# those exact tokens appear in the job text.
SEMANTIC_SKILL_GROUPS: list[set[str]] = [
    {"computer vision", "yolo", "opencv", "object detection", "image classification", "onnx", "image processing"},
    {"pytorch", "tensorflow", "keras", "deep learning", "neural networks", "machine learning"},
    {"nlp", "natural language processing", "llm", "large language models", "transformers", "llm fine-tuning"},
    {"react", "next.js", "frontend", "vue", "javascript", "typescript"},
    {"aws", "gcp", "azure", "cloud", "cloud infrastructure"},
    {"docker", "kubernetes", "containerization", "devops", "ci/cd"},
    {"backend", "django", "fastapi", "flask", "spring boot", "node.js", "api development"},
    {"sql", "postgresql", "mysql", "database", "data modeling"},
]


def canonical_skill_name(name: str) -> str:
    return name.strip()


def infer_category(name: str) -> SkillCategory:
    return SKILL_CATALOG.get(canonical_skill_name(name), SkillCategory.OTHER)


def is_ai_ml_skill(name: str) -> bool:
    return infer_category(name) == SkillCategory.AI_ML
