"""How well a job's title fits the roles a candidate says they want.

Skill overlap alone can't tell a Computer Vision Engineer that a "Packaging
Design Internship" isn't for them when both mention Python. Real job boards
mix engineering, sales, legal, and operations roles, so the title has to
count. Kept as transparent token overlap plus coarse role families -- no
opaque model -- in line with the rest of the matching engine.
"""

import re

# Phrase normalization applied before tokenizing (English and Japanese).
_PHRASES = [
    (r"machine[- ]learning|機械学習", " ml "),
    (r"artificial intelligence", " ai "),
    (r"front[- ]?end|フロントエンド", " frontend "),
    (r"back[- ]?end|バックエンド", " backend "),
    (r"full[- ]?stack|フルスタック", " fullstack "),
    (r"site reliability", " sre "),
    (r"computer vision|コンピュータ[ー]?ビジョン|画像認識", " cv "),
    (r"natural language processing", " nlp "),
    (r"data scien(ce|tist)|データサイエンティスト", " data scientist "),
    (r"developer|programmer|エンジニア|開発者|プログラマー|開発", " engineer "),
    (r"ソフトウェア", " software "),
    (r"研究", " research "),
    (r"データ", " data "),
    (r"営業|セールス", " sales "),
    (r"マネージャー|マネジャー", " manager "),
    (r"デザイナー", " designer "),
    (r"プロダクト", " product "),
    (r"インフラ", " infrastructure "),
]
_STOPWORDS = {
    "senior", "sr", "junior", "jr", "lead", "staff", "principal", "head", "chief", "of", "the", "and", "for", "in",
    "at", "a", "an", "to", "with", "intern", "internship", "new", "graduate", "grad", "jp", "japan", "tokyo", "osaka",
    "based", "remote", "hybrid", "i", "ii", "iii", "iv", "level", "team", "specialist", "associate", "mid",
}

_ENGINEERING = {
    "engineer", "engineering", "software", "ml", "ai", "data", "scientist", "researcher", "research", "sre", "devops",
    "architect", "frontend", "backend", "fullstack", "cv", "nlp", "infrastructure", "platform", "security",
    "robotics", "embedded", "firmware", "qa", "sdet", "llm",
}
_BUSINESS = {
    "sales", "account", "executive", "ae", "bdr", "sdr", "partner", "partnerships", "marketing", "recruiter",
    "recruiting", "talent", "legal", "counsel", "finance", "accountant", "hr", "people", "communications",
    "customer", "success", "support", "operations", "business", "development", "alliances", "procurement",
}

_FAMILY_FLOOR = 0.35


def _tokens(title: str) -> set[str]:
    text = title.lower()
    for pattern, replacement in _PHRASES:
        text = re.sub(pattern, replacement, text)
    words = re.findall(r"[a-z0-9+#.]+", text)
    return {w.strip(".") for w in words if w.strip(".") and w not in _STOPWORDS}


def _family(tokens: set[str]) -> str | None:
    # Engineering wins ties, so "Sales Engineer" or "Solutions Architect"
    # still counts as technical.
    if tokens & _ENGINEERING:
        return "engineering"
    if tokens & _BUSINESS:
        return "business"
    return None


def role_relevance(job_title: str, desired_roles: list[str]) -> float | None:
    """0..1 fit between a job title and the candidate's desired roles, or None
    when the candidate hasn't said what they want (then it isn't scored)."""
    wanted = [_tokens(role) for role in desired_roles if role.strip()]
    wanted = [tokens for tokens in wanted if tokens]
    if not wanted:
        return None

    title_tokens = _tokens(job_title)
    best = max(len(tokens & title_tokens) / len(tokens) for tokens in wanted)

    title_family = _family(title_tokens)
    if title_family and any(_family(tokens) == title_family for tokens in wanted):
        best = max(best, _FAMILY_FLOOR)
    return round(min(1.0, best), 3)
