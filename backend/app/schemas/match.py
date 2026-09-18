from datetime import datetime

from pydantic import BaseModel

from app.models.enums import MatchStrength, RequirementState
from app.schemas.job import JobCard


class RequirementItem(BaseModel):
    label: str
    category: str
    state: RequirementState
    detail: str


class MatchOut(BaseModel):
    id: str
    job: JobCard
    deterministic_pass: bool
    semantic_score: float
    overall_score: float
    match_strength: MatchStrength
    requirement_breakdown: list[RequirementItem]
    ai_explanation: str | None
    computed_at: datetime

    model_config = {"from_attributes": True}


class MatchListResponse(BaseModel):
    items: list[MatchOut]
    total: int
