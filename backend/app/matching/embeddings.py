"""Lightweight, explainable "semantic similarity" without a hosted embedding
model or API key.

Rather than opaque dense vectors, we build a concept vector: one dimension
per catalog skill plus one per semantic skill group (see skill_taxonomy.py).
A job description and a user's skill list both get projected into this same
space, and cosine similarity between the two gives Stage 2 of the matching
engine (master spec section 12). Because every dimension has a name, the
matching engine can report *which* concept groups drove a match instead of
producing a mystery score.

The vector is stored on JobEmbedding so this only has to be computed once per
job description (keyed by content hash), matching the cost-control principle
in section 41. Swapping in a hosted embedding model later only requires a new
EmbeddingProvider implementation with the same `vectorize` signature.
"""

import hashlib
import re

import numpy as np

from app.matching.skill_taxonomy import SEMANTIC_SKILL_GROUPS, SKILL_CATALOG

_SKILL_DIMENSIONS = sorted(SKILL_CATALOG.keys())
_GROUP_DIMENSIONS = list(range(len(SEMANTIC_SKILL_GROUPS)))
VECTOR_SIZE = len(_SKILL_DIMENSIONS) + len(_GROUP_DIMENSIONS)


def _tokenize(text: str) -> str:
    return re.sub(r"[^a-z0-9\+\.# ]", " ", text.lower())


def vectorize_text(text: str) -> list[float]:
    lowered = _tokenize(text)
    vector = np.zeros(VECTOR_SIZE, dtype=float)

    for i, skill in enumerate(_SKILL_DIMENSIONS):
        if skill.lower() in lowered:
            vector[i] = 1.0

    offset = len(_SKILL_DIMENSIONS)
    for i, group in enumerate(SEMANTIC_SKILL_GROUPS):
        if any(term in lowered for term in group):
            vector[offset + i] = 1.0

    return vector.tolist()


def vectorize_skills(skill_names: list[str]) -> list[float]:
    joined = " ".join(skill_names)
    return vectorize_text(joined)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    va, vb = np.array(a), np.array(b)
    norm = np.linalg.norm(va) * np.linalg.norm(vb)
    if norm == 0:
        return 0.0
    return float(np.dot(va, vb) / norm)


def matched_concept_groups(job_vector: list[float], user_vector: list[float]) -> list[str]:
    """Human-readable labels for which semantic groups both sides share."""
    offset = len(_SKILL_DIMENSIONS)
    labels = []
    for i, group in enumerate(SEMANTIC_SKILL_GROUPS):
        if job_vector[offset + i] > 0 and user_vector[offset + i] > 0:
            labels.append(sorted(group)[0])
    return labels


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
