import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PolicyBase(BaseModel):
    title: str
    description: str | None = None
    content: str | None = None


class PolicyCreate(PolicyBase):
    pass


class PolicyUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    content: str | None = None
    status: str | None = None


class PolicyRead(PolicyBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    version: int
    status: str
    created_at: datetime
    updated_at: datetime
