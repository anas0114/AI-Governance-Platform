import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditCreate(BaseModel):
    ai_system_id: uuid.UUID
    title: str


class AuditRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ai_system_id: uuid.UUID
    title: str
    status: str
    created_at: datetime


class AuditFindingCreate(BaseModel):
    audit_id: uuid.UUID
    severity: str = "low"
    description: str
    remediation: str | None = None


class AuditFindingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    audit_id: uuid.UUID
    severity: str
    description: str
    remediation: str | None
    status: str
    created_at: datetime
