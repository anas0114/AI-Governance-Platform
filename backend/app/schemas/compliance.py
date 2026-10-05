import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ComplianceAssessmentCreate(BaseModel):
    ai_system_id: uuid.UUID
    framework_id: uuid.UUID


class ComplianceAssessmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ai_system_id: uuid.UUID
    framework_id: uuid.UUID
    status: str
    score: str | None
    created_at: datetime


class ComplianceFrameworkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
