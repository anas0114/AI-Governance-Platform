import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AISystemBase(BaseModel):
    name: str
    description: str | None = None
    owner: str | None = None
    risk_level: str = "unclassified"
    lifecycle_stage: str = "development"


class AISystemCreate(AISystemBase):
    pass


class AISystemRead(AISystemBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
