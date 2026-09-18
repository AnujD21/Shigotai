"""Rule-based extraction provider used when no LLM API key is configured.

This is intentionally conservative: it only reports a field when the source
text contains clear evidence for it. It never guesses. This keeps the app
fully functional offline while honoring the "never invent a requirement"
product rule (master spec section 9 & 50).
"""

import re

from app.ai.base import ExtractionJSON, LLMProvider
from app.matching.skill_taxonomy import SKILL_CATALOG

_JLPT_PATTERN = re.compile(r"(?:JLPT\s*)?N([1-5])", re.IGNORECASE)
_JLPT_JA_PATTERN = re.compile(r"日本語(?:能力|能力試験)?\s*N([1-5])")
_EXPERIENCE_PATTERN = re.compile(r"(\d+)\+?\s*(?:years?|年)\b")
_PREFERRED_MARKERS = [
    "preferred", "nice to have", "nice-to-have", "a plus", "bonus", "歓迎", "尚可", "望ましい",
]
_REQUIRED_MARKERS = ["required", "must have", "must-have", "essential", "必須"]
_NEW_GRAD_POSITIVE = ["new graduate", "new grad", "fresher", "entry level", "entry-level", "新卒", "第二新卒"]
_NEW_GRAD_NEGATIVE = ["experienced candidates only", "no new graduates", "経験者のみ"]
_VISA_POSITIVE = ["visa sponsorship available", "will sponsor", "sponsorship provided", "visa support available", "ビザサポートあり", "就労ビザ支援"]
_VISA_NEGATIVE = ["no visa sponsorship", "sponsorship not available", "must have existing work visa", "ビザサポートなし"]
_EDUCATION_PATTERNS = [
    (re.compile(r"bachelor'?s?\s+degree|学士", re.IGNORECASE), "Bachelor's degree"),
    (re.compile(r"master'?s?\s+degree|修士", re.IGNORECASE), "Master's degree"),
    (re.compile(r"\bph\.?d\b|博士", re.IGNORECASE), "PhD"),
]
_BUSINESS_JAPANESE_PATTERN = re.compile(
    r"business[- ]level japanese|business japanese|ビジネスレベルの?日本語|日本語(での)?ビジネスコミュニケーション",
    re.IGNORECASE,
)
_BUSINESS_ENGLISH_PATTERN = re.compile(r"business[- ]level english|business english|ビジネスレベルの?英語", re.IGNORECASE)


def _find_skills(text_lower: str) -> list[str]:
    found = []
    for skill in SKILL_CATALOG:
        if skill.lower() in text_lower:
            found.append(skill)
    return found


def _split_required_preferred(description: str) -> tuple[str, str]:
    lowered = description.lower()
    split_index = None
    for marker in _PREFERRED_MARKERS:
        idx = lowered.find(marker)
        if idx != -1 and (split_index is None or idx < split_index):
            split_index = idx
    if split_index is None:
        return description, ""
    return description[:split_index], description[split_index:]


class DevLLMProvider(LLMProvider):
    def extract_requirements(self, job_title: str, description: str, language: str) -> ExtractionJSON:
        required_text, preferred_text = _split_required_preferred(description)
        required_skills = _find_skills(required_text.lower())
        preferred_skills = [s for s in _find_skills(preferred_text.lower()) if s not in required_skills]

        jlpt_match = _JLPT_JA_PATTERN.search(description) or _JLPT_PATTERN.search(description)
        jlpt_requirement = f"N{jlpt_match.group(1)}" if jlpt_match else None

        japanese_requirement = None
        if _BUSINESS_JAPANESE_PATTERN.search(description):
            japanese_requirement = "Business-level Japanese communication required"
        elif jlpt_requirement:
            japanese_requirement = f"JLPT {jlpt_requirement}+ required"

        english_requirement = "Business-level English required" if _BUSINESS_ENGLISH_PATTERN.search(description) else None

        exp_match = _EXPERIENCE_PATTERN.search(description)
        minimum_experience = float(exp_match.group(1)) if exp_match else None

        education_requirement = None
        for pattern, label in _EDUCATION_PATTERNS:
            if pattern.search(description):
                education_requirement = label
                break

        lowered = description.lower()
        new_graduate_allowed: bool | None = None
        if any(marker in lowered for marker in _NEW_GRAD_POSITIVE):
            new_graduate_allowed = True
        elif any(marker in lowered for marker in _NEW_GRAD_NEGATIVE):
            new_graduate_allowed = False

        visa_sponsorship = "NOT_STATED"
        if any(marker in lowered for marker in _VISA_POSITIVE):
            visa_sponsorship = "YES"
        elif any(marker in lowered for marker in _VISA_NEGATIVE):
            visa_sponsorship = "NO"

        return ExtractionJSON(
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            minimum_experience=minimum_experience,
            education_requirement=education_requirement,
            jlpt_requirement=jlpt_requirement,
            japanese_requirement=japanese_requirement,
            english_requirement=english_requirement,
            new_graduate_allowed=new_graduate_allowed,
            visa_sponsorship=visa_sponsorship,
        )

    def explain_match(
        self,
        job_title: str,
        company_name: str,
        requirement_breakdown: list[dict],
        match_strength: str,
    ) -> str:
        matched = [r["label"] for r in requirement_breakdown if r["state"] == "MATCH"]
        missing = [r["label"] for r in requirement_breakdown if r["state"] == "MISSING"]
        partial = [r["label"] for r in requirement_breakdown if r["state"] == "PARTIAL"]

        parts = []
        if matched:
            parts.append(f"You meet {len(matched)} of the stated requirements, including {', '.join(matched[:4])}.")
        if partial:
            parts.append(f"You partially meet: {', '.join(partial[:3])}.")
        if missing:
            parts.append(f"The role also asks for {', '.join(missing[:3])}, which isn't reflected in your profile yet.")
        if not parts:
            parts.append("There isn't enough information in your profile yet to compare against this role.")

        strength_sentence = {
            "STRONG_MATCH": f"Overall, this looks like a strong match for the {job_title} role at {company_name}.",
            "PARTIAL_MATCH": f"Overall, this is a partial match for the {job_title} role at {company_name} -- worth reviewing the gaps below.",
            "SIGNIFICANT_GAPS": f"Overall, there are significant gaps between your profile and this {job_title} role at {company_name}.",
        }.get(match_strength, "")

        return " ".join(parts + ([strength_sentence] if strength_sentence else []))
