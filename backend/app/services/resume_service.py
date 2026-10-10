"""Resume parsing (master spec section 4).

Two stages:

1. Text extraction -- pypdf for PDFs; python-docx for DOCX, including tables,
   headers, and footers, where many resume templates put most of their
   content.
2. Structuring -- an LLM with a strict output schema when one is configured
   (see app/ai/provider.py), otherwise the conservative heuristics below.
   LLM output is then checked against the resume text: an education,
   employer, or certification that doesn't appear in the document is dropped
   rather than shown, because a hallucinated degree is worse than a missing
   one.

Results are presented to the user as suggestions to accept/edit/remove, never
written directly into their profile. When a section can't be confidently
parsed, we surface a warning instead of guessing.
"""

import io
import logging
import re
import unicodedata

import pypdf
from docx import Document

from app.ai.provider import get_resume_llm_provider
from app.ai.schemas import ResumeLLMExtraction
from app.matching.skill_taxonomy import (
    SKILL_ALIASES,
    canonical_skill_name,
    find_skills,
    is_ai_ml_skill,
    term_pattern,
)
from app.models.enums import JLPTLevel
from app.schemas.profile import (
    CertificationIn,
    EducationIn,
    ExperienceIn,
    ProjectIn,
    ResumeExtractionResult,
    SkillIn,
)

logger = logging.getLogger(__name__)

_SECTION_HEADERS = {
    "education": re.compile(r"^\s*(education|学歴)\s*$", re.IGNORECASE),
    "experience": re.compile(r"^\s*(?:(?:work|professional)\s+experience|experience|職歴|職務経歴)\s*$", re.IGNORECASE),
    "projects": re.compile(r"^\s*projects?\s*$", re.IGNORECASE),
    "certifications": re.compile(r"^\s*(certifications?|licenses?|資格|免許)\s*$", re.IGNORECASE),
    "skills": re.compile(r"^\s*(?:(?:technical\s+)?skills|スキル)\s*$", re.IGNORECASE),
}
_DEGREE_PATTERN = re.compile(
    r"(Bachelor(?:'s)?|Master(?:'s)?|B\.?Tech|M\.?Tech|B\.?S\.?|M\.?S\.?|Ph\.?D)[^\n,]{0,80}", re.IGNORECASE
)
_UNIVERSITY_PATTERN = re.compile(r"[^\n]*\b(University|Institute|College)\b[^\n]*", re.IGNORECASE)
_YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")
_JLPT_PATTERN = re.compile(r"JLPT\s*N([1-5])|N([1-5])\s*JLPT|日本語能力試験\s*N([1-5])", re.IGNORECASE)
_URL_PATTERN = re.compile(r"https?://[^\s)]+")
_CERT_KEYWORDS = ["AWS Certified", "Oracle Certified", "NPTEL", "Google Cloud", "Azure Certified", "PMP", "CFA"]

# ~8k tokens: far more than any real resume, while bounding what one upload
# can cost on a paid LLM or consume of a free tier's daily budget.
_MAX_LLM_CHARS = 30_000


# --------------------------------------------------------------------------
# Text extraction
# --------------------------------------------------------------------------


def _docx_text(content: bytes) -> str:
    document = Document(io.BytesIO(content))
    parts: list[str] = []
    for section in document.sections:
        parts.extend(p.text for p in section.header.paragraphs)
    parts.extend(p.text for p in document.paragraphs)
    for table in document.tables:
        for row in table.rows:
            seen: set[int] = set()
            cells = []
            for cell in row.cells:
                # Merged cells repeat the same object across the row.
                if id(cell._tc) not in seen:
                    seen.add(id(cell._tc))
                    cells.append(cell.text.strip())
            parts.append(" | ".join(c for c in cells if c))
    for section in document.sections:
        parts.extend(p.text for p in section.footer.paragraphs)
    return "\n".join(parts)


def extract_text(filename: str, content: bytes) -> str:
    lowered = filename.lower()
    if lowered.endswith(".pdf"):
        try:
            reader = pypdf.PdfReader(io.BytesIO(content))
            if reader.is_encrypted:
                reader.decrypt("")
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:  # pypdf raises a variety of errors on malformed files
            raise ValueError("We couldn't open this PDF. Try exporting it again, or upload a DOCX.") from exc
    elif lowered.endswith(".docx"):
        try:
            text = _docx_text(content)
        except Exception as exc:
            raise ValueError("We couldn't open this DOCX file. Try saving it again, or upload a PDF.") from exc
    else:
        raise ValueError("Unsupported resume format. Please upload a PDF or DOCX file.")
    # NFKC folds full-width characters common in Japanese resumes (Ｐｙｔｈｏｎ, ２０２３).
    text = unicodedata.normalize("NFKC", text)
    return re.sub(r"[ \t]+", " ", text).strip()


# --------------------------------------------------------------------------
# Heuristic fallback
# --------------------------------------------------------------------------


def _split_sections(text: str) -> dict[str, str]:
    lines = text.splitlines()
    sections: dict[str, list[str]] = {}
    current = "header"
    sections[current] = []
    for line in lines:
        matched_section = None
        for name, pattern in _SECTION_HEADERS.items():
            if pattern.match(line.strip()):
                matched_section = name
                break
        if matched_section:
            current = matched_section
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return {name: "\n".join(content_lines) for name, content_lines in sections.items()}


def _skill_entries(names: list[str]) -> list[SkillIn]:
    return [SkillIn(name=name, is_ai_ml=is_ai_ml_skill(name)) for name in names]


def _extract_education(section_text: str) -> list[EducationIn]:
    results = []
    for block in re.split(r"\n\s*\n", section_text):
        degree_match = _DEGREE_PATTERN.search(block)
        if not degree_match:
            continue
        university_match = _UNIVERSITY_PATTERN.search(block)
        year_matches = _YEAR_PATTERN.findall(block)
        results.append(
            EducationIn(
                degree=degree_match.group(0).strip(" ,"),
                university=university_match.group(0).strip() if university_match else "Not detected",
                graduation_year=int(year_matches[-1]) if year_matches else None,
            )
        )
    return results


def _extract_certifications(section_text: str, full_text: str) -> list[CertificationIn]:
    results = []
    seen = set()
    combined = section_text + "\n" + full_text
    jlpt_match = _JLPT_PATTERN.search(combined)
    if jlpt_match:
        level = next(g for g in jlpt_match.groups() if g)
        results.append(CertificationIn(name=f"JLPT N{level}", issuer="Japan Foundation"))
        seen.add(f"jlpt n{level}")
    for keyword in _CERT_KEYWORDS:
        if keyword.lower() in combined.lower() and keyword.lower() not in seen:
            results.append(CertificationIn(name=keyword))
            seen.add(keyword.lower())
    return results


def _extract_projects(section_text: str) -> list[ProjectIn]:
    results = []
    for block in re.split(r"\n\s*\n", section_text.strip()):
        lines = [line.strip("-* \t") for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        name = lines[0][:120]
        description = " ".join(lines[1:])[:600] or None
        urls = _URL_PATTERN.findall(block)
        github_url = next((u for u in urls if "github.com" in u), None)
        project_url = next((u for u in urls if u != github_url), None)
        results.append(
            ProjectIn(
                name=name,
                description=description,
                technologies=find_skills(block),
                github_url=github_url,
                project_url=project_url,
            )
        )
    return results


def _extract_jlpt_level(full_text: str) -> JLPTLevel | None:
    match = _JLPT_PATTERN.search(full_text)
    if not match:
        return None
    level = next(g for g in match.groups() if g)
    return JLPTLevel(f"N{level}")


def _heuristic_parse(text: str, filename: str, warnings: list[str]) -> ResumeExtractionResult:
    sections = _split_sections(text)
    education = _extract_education(sections.get("education", "") or text)
    if not education:
        warnings.append("We couldn't confidently detect an education entry. Please add it manually.")

    skills = _skill_entries(find_skills(text))
    if not skills:
        warnings.append("We couldn't detect any recognized skills. You can add them manually below.")
    if sections.get("experience", "").strip():
        warnings.append("Work experience needs manual review -- automatic parsing of roles and dates isn't reliable enough yet.")

    return ResumeExtractionResult(
        education=education,
        experience=[],
        projects=_extract_projects(sections.get("projects", "")),
        certifications=_extract_certifications(sections.get("certifications", ""), text),
        skills=skills,
        jlpt_level=_extract_jlpt_level(text),
        source_filename=filename,
        warnings=warnings,
        extraction_method="rules",
    )


# --------------------------------------------------------------------------
# LLM extraction + grounding
# --------------------------------------------------------------------------


def _normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).lower()
    return re.sub(r"[\s\W_]+", " ", value).strip()


class _Grounding:
    """Checks that a value the model returned is actually in the resume."""

    def __init__(self, text: str):
        self.raw = text
        self.normalized = f" {_normalize(text)} "
        self.compact = self.normalized.replace(" ", "")
        self.tokens = set(self.normalized.split())

    def contains(self, value: str | None) -> bool:
        if not value:
            return False
        normalized = _normalize(value)
        if not normalized:
            return False
        if f" {normalized} " in self.normalized or normalized.replace(" ", "") in self.compact:
            return True
        # Tolerate abbreviations and reordering ("IIT Bombay" vs "Indian
        # Institute of Technology, Bombay"): most significant words present.
        significant = [t for t in normalized.split() if len(t) >= 3]
        if not significant:
            return False
        return sum(t in self.tokens for t in significant) / len(significant) >= 0.6

    def has_skill(self, name: str) -> bool:
        terms = [name, *SKILL_ALIASES.get(name, [])]
        return any(term_pattern(term).search(self.raw) for term in terms) or self.contains(name)

    def has_url(self, url: str | None) -> bool:
        return bool(url) and url.rstrip("/").lower() in self.raw.lower()


def _grounded_result(llm: ResumeLLMExtraction, text: str, filename: str, warnings: list[str]) -> ResumeExtractionResult:
    grounding = _Grounding(text)
    dropped = 0

    education = []
    for e in llm.education:
        if grounding.contains(e.university):
            education.append(
                EducationIn(
                    degree=e.degree,
                    university=e.university,
                    field_of_study=e.field_of_study,
                    graduation_year=e.graduation_year,
                    is_current_student=e.is_current_student,
                )
            )
        else:
            dropped += 1

    experience = []
    for x in llm.experience:
        if grounding.contains(x.company_name):
            experience.append(
                ExperienceIn(
                    company_name=x.company_name,
                    role=x.role,
                    is_internship=x.is_internship,
                    start_date=x.start_date,
                    end_date=x.end_date,
                    description=x.description,
                )
            )
        else:
            dropped += 1

    projects = [
        ProjectIn(
            name=p.name[:120],
            description=(p.description or None) and p.description[:600],
            technologies=[canonical_skill_name(t) for t in p.technologies if grounding.has_skill(canonical_skill_name(t))],
            github_url=p.github_url if grounding.has_url(p.github_url) else None,
            project_url=p.project_url if grounding.has_url(p.project_url) else None,
        )
        for p in llm.projects
        if grounding.contains(p.name)
    ]
    dropped += len(llm.projects) - len(projects)

    certifications = []
    for c in llm.certifications:
        if grounding.contains(c.name):
            certifications.append(CertificationIn(name=c.name, issuer=c.issuer, year=c.year))
        else:
            dropped += 1

    skill_names: list[str] = []
    for raw_name in llm.skills:
        name = canonical_skill_name(raw_name)
        if name and name not in skill_names and grounding.has_skill(name):
            skill_names.append(name)
    # The deterministic detector catches catalog skills the model skipped.
    for name in find_skills(text):
        if name not in skill_names:
            skill_names.append(name)

    jlpt = None
    if llm.jlpt_level and re.search(rf"(?<![A-Za-z0-9]){llm.jlpt_level}(?![0-9])", text, re.IGNORECASE):
        jlpt = JLPTLevel(llm.jlpt_level)

    years = llm.total_years_of_experience
    if years is not None and not 0 <= years <= 50:
        years = None

    if dropped:
        warnings.append(
            f"We left out {dropped} item{'s' if dropped != 1 else ''} we couldn't match to text in your resume. "
            "Add anything missing manually."
        )
    if not education:
        warnings.append("We couldn't confidently detect an education entry. Please add it manually.")

    return ResumeExtractionResult(
        education=education,
        experience=experience,
        projects=projects,
        certifications=certifications,
        skills=_skill_entries(skill_names),
        jlpt_level=jlpt,
        years_of_experience=years,
        source_filename=filename,
        warnings=warnings,
        extraction_method="ai",
    )


def parse_resume(filename: str, content: bytes) -> ResumeExtractionResult:
    warnings: list[str] = []
    text = extract_text(filename, content)
    if not text.strip():
        warnings.append(
            "We couldn't read any text from this file -- it may be a scanned image. "
            "Try a PDF exported from Word or Google Docs, or a DOCX."
        )
        return ResumeExtractionResult(
            education=[], experience=[], projects=[], certifications=[], skills=[],
            source_filename=filename, warnings=warnings, extraction_method="rules",
        )

    provider = get_resume_llm_provider()
    if provider.is_llm:
        llm_text = text[:_MAX_LLM_CHARS]
        if len(text) > _MAX_LLM_CHARS:
            warnings.append("Your resume is unusually long, so we only analyzed the first part of it.")
        extraction = provider.extract_resume(llm_text)
        if extraction is not None:
            return _grounded_result(extraction, text, filename, warnings)
        logger.warning("LLM resume extraction failed; falling back to heuristics")

    return _heuristic_parse(text, filename, warnings)
