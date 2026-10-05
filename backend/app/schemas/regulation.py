import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class RegulationBase(BaseModel):
    title: str
    jurisdiction: str | None = None
    category: str | None = None
    summary: str | None = None
    source_url: str | None = None
    effective_date: date | None = None
    status: str = "tracked"


class RegulationCreate(RegulationBase):
    pass


class RegulationUpdate(BaseModel):
    title: str | None = None
    jurisdiction: str | None = None
    category: str | None = None
    summary: str | None = None
    source_url: str | None = None
    effective_date: date | None = None
    status: str | None = None


class RegulationRead(RegulationBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class RegulationClauseBase(BaseModel):
    clause_number: str
    title: str | None = None
    text: str


class RegulationClauseCreate(RegulationClauseBase):
    pass


class RegulationClauseRead(RegulationClauseBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    regulation_id: uuid.UUID
    created_at: datetime
