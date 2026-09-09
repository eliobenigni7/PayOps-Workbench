from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import ImprovementStatus, ReasonCode, ResolutionOutcome


class ResolveRequest(BaseModel):
    outcome: ResolutionOutcome
    reason_code: ReasonCode
    note: str | None = None
    resolved_by: str = Field(min_length=1)


class OpportunityStatusRequest(BaseModel):
    status: ImprovementStatus


class HealthResponse(BaseModel):
    status: str
    ai_available: bool
    time: datetime
