"""Rule-based extraction provider used when no LLM API key is configured.

This is intentionally conservative: it only reports a field when the source
text contains clear evidence for it. It never guesses. This keeps the app
fully functional offline while honoring the "never invent a requirement"
product rule (master spec section 9 & 50).
"""

import re

from app.ai.base import ExtractionJSON, LLMProvider
from app.matching.skill_taxonomy import find_skills

# "N2" only counts as a JLPT level when it stands alone (not "N2O", "4N2") and
# sits next to Japanese-language context -- real postings contain plenty of
# other N-numbers (product codes, model names).
_JLPT_PATTERN = re.compile(r"(?<![A-Za-z0-9])(JLPT\s*)?N([1-5])(?![0-9A-Za-z])", re.IGNORECASE)
_JLPT_JA_PATTERN = re.compile(r"日本語(?:能力|能力試験)?\s*N([1-5])")
_JLPT_CONTEXT = re.compile(r"japanese|jlpt|日本語|level|レベル|以上|相当", re.IGNORECASE)
# Years of experience: 1-2 digits (never a calendar year like 2026年), and
# only when "experience" is nearby so "100 years of history" doesn't count.
_EXPERIENCE_EN_PATTERN = re.compile(
    r"(?<!\d)(\d{1,2})\s*\+?\s*(?:or more\s+|plus\s+)?years?\b(?=[^.\n]{0,40}\bexperience)", re.IGNORECASE
)
_EXPERIENCE_JA_PATTERN = re.compile(r"経験[^。\n]{0,20}?(?<!\d)(\d{1,2})\s*年以上")
_MAX_PLAUSIBLE_EXPERIENCE = 15
_PREFERRED_MARKERS = [
    "preferred", "nice to have", "nice-to-have", "a plus", "bonus", "歓迎", "尚可", "望ましい",
]
_REQUIRED_MARKERS = ["required", "must have", "must-have", "essential", "必須"]
_NEW_GRAD_POSITIVE = ["new graduate", "new grad", "fresher", "entry level", "entry-level", "新卒", "第二新卒"]
_NEW_GRAD_NEGATIVE = ["experienced candidates only", "no new graduates", "経験者のみ"]
_VISA_POSITIVE = [
    "visa sponsorship available", "visa sponsorship is available", "will sponsor", "we sponsor", "sponsorship provided",
    "visa support available", "visa support is available", "ビザサポートあり", "就労ビザ支援", "ビザ取得サポート",
]
# Checked before the positive markers: "no visa sponsorship available" must
# not be read as an offer just because it contains "visa sponsorship available".
_VISA_NEGATIVE = [
    "no visa sponsorship", "sponsorship not available", "sponsorship is not available", "must have existing work visa",
    "unable to sponsor", "cannot sponsor", "can't sponsor", "not able to sponsor", "does not sponsor",
    "do not sponsor", "not offer visa sponsorship", "no visa support", "ビザサポートなし", "ビザサポートはありません",
]
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


def _find_jlpt(description: str) -> str | None:
    ja = _JLPT_JA_PATTERN.search(description)
    if ja:
        return f"N{ja.group(1)}"
    for match in _JLPT_PATTERN.finditer(description):
        window = description[max(0, match.start() - 40) : match.end() + 40]
        if match.group(1) or _JLPT_CONTEXT.search(window):
            return f"N{match.group(2)}"
    return None


def _find_minimum_experience(description: str) -> float | None:
    for pattern in (_EXPERIENCE_EN_PATTERN, _EXPERIENCE_JA_PATTERN):
        for match in pattern.finditer(description):
            years = int(match.group(1))
            if 0 < years <= _MAX_PLAUSIBLE_EXPERIENCE:
                return float(years)
    return None


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
        required_skills = find_skills(required_text)
        preferred_skills = [s for s in find_skills(preferred_text) if s not in required_skills]

        jlpt_requirement = _find_jlpt(description)

        japanese_requirement = None
        if _BUSINESS_JAPANESE_PATTERN.search(description):
            japanese_requirement = "Business-level Japanese communication required"
        elif jlpt_requirement:
            japanese_requirement = f"JLPT {jlpt_requirement}+ required"

        english_requirement = "Business-level English required" if _BUSINESS_ENGLISH_PATTERN.search(description) else None

        minimum_experience = _find_minimum_experience(description)

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
        if any(marker in lowered for marker in _VISA_NEGATIVE):
            visa_sponsorship = "NO"
        elif any(marker in lowered for marker in _VISA_POSITIVE):
            visa_sponsorship = "YES"

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
