import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CollaborationRequest(BaseModel):
    query: str
    session_id: str | None = None


class CollaborationStepRead(BaseModel):
    agent_name: str
    output: str
    duration_ms: float | None = None
    events: list[dict] = []


class CollaborationResponse(BaseModel):
    run_id: uuid.UUID
    session_id: str
    query: str
    final_recommendation: str
    steps: list[CollaborationStepRead]


class CollaborationRunSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    query: str
    session_id: str
    final_recommendation: str | None
    created_at: datetime
