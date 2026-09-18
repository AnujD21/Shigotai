"""Resume parsing (master spec section 4).

Extraction here is intentionally heuristic and conservative: it is presented
to the user as suggestions to accept/edit/remove, never written directly into
their profile. When a section can't be confidently parsed, we surface a
warning instead of guessing.
"""

import io
import re

import pypdf
from docx import Document

from app.matching.skill_taxonomy import SKILL_CATALOG, is_ai_ml_skill
from app.models.enums import JLPTLevel
from app.schemas.profile import CertificationIn, EducationIn, ProjectIn, ResumeExtractionResult, SkillIn

_SECTION_HEADERS = {
    "education": re.compile(r"^\s*education\s*$", re.IGNORECASE),
    "experience": re.compile(r"^\s*(work\s+)?experience\s*$", re.IGNORECASE),
    "projects": re.compile(r"^\s*projects?\s*$", re.IGNORECASE),
    "certifications": re.compile(r"^\s*(certifications?|licenses?)\s*$", re.IGNORECASE),
    "skills": re.compile(r"^\s*(technical\s+)?skills\s*$", re.IGNORECASE),
}
_DEGREE_PATTERN = re.compile(
    r"(Bachelor(?:'s)?|Master(?:'s)?|B\.?Tech|M\.?Tech|B\.?S\.?|M\.?S\.?|Ph\.?D)[^\n,]{0,80}", re.IGNORECASE
)
_UNIVERSITY_PATTERN = re.compile(r"[^\n]*\b(University|Institute|College)\b[^\n]*", re.IGNORECASE)
_YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")
_JLPT_PATTERN = re.compile(r"JLPT\s*N([1-5])|N([1-5])\s*JLPT|日本語能力試験\s*N([1-5])", re.IGNORECASE)
_URL_PATTERN = re.compile(r"https?://[^\s)]+")
_CERT_KEYWORDS = ["AWS Certified", "Oracle Certified", "NPTEL", "Google Cloud", "Azure Certified", "PMP", "CFA"]


def extract_text(filename: str, content: bytes) -> str:
    if filename.lower().endswith(".pdf"):
        reader = pypdf.PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if filename.lower().endswith(".docx"):
        document = Document(io.BytesIO(content))
        return "\n".join(p.text for p in document.paragraphs)
    raise ValueError("Unsupported resume format. Please upload a PDF or DOCX file.")


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


def _extract_skills(full_text: str) -> list[SkillIn]:
    lowered = full_text.lower()
    return [
        SkillIn(name=skill, is_ai_ml=is_ai_ml_skill(skill))
        for skill in SKILL_CATALOG
        if skill.lower() in lowered
    ]


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
        technologies = [skill for skill in SKILL_CATALOG if skill.lower() in block.lower()]
        urls = _URL_PATTERN.findall(block)
        github_url = next((u for u in urls if "github.com" in u), None)
        project_url = next((u for u in urls if u != github_url), None)
        results.append(
            ProjectIn(name=name, description=description, technologies=technologies, github_url=github_url, project_url=project_url)
        )
    return results


def _extract_jlpt_level(full_text: str) -> JLPTLevel | None:
    match = _JLPT_PATTERN.search(full_text)
    if not match:
        return None
    level = next(g for g in match.groups() if g)
    return JLPTLevel(f"N{level}")


def parse_resume(filename: str, content: bytes) -> ResumeExtractionResult:
    warnings: list[str] = []
    text = extract_text(filename, content)
    if not text.strip():
        warnings.append("We couldn't read any text from this file -- it may be a scanned image.")

    sections = _split_sections(text)
    education = _extract_education(sections.get("education", "") or text)
    if not education:
        warnings.append("We couldn't confidently detect an education entry. Please add it manually.")

    projects = _extract_projects(sections.get("projects", ""))
    certifications = _extract_certifications(sections.get("certifications", ""), text)
    skills = _extract_skills(text)
    if not skills:
        warnings.append("We couldn't detect any recognized skills. You can add them manually below.")
    if sections.get("experience", "").strip():
        warnings.append("Work experience needs manual review -- automatic parsing of roles and dates isn't reliable enough yet.")

    return ResumeExtractionResult(
        education=education,
        experience=[],
        projects=projects,
        certifications=certifications,
        skills=skills,
        jlpt_level=_extract_jlpt_level(text),
        source_filename=filename,
        warnings=warnings,
    )
