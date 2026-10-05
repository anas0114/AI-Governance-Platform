import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResearchNoteBase(BaseModel):
    title: str
    content: str
    tags: str | None = None


class ResearchNoteCreate(ResearchNoteBase):
    pass


class ResearchNoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    tags: str | None = None


class ResearchNoteRead(ResearchNoteBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ResearchQuerySource(BaseModel):
    document_id: str
    snippet: str


class ResearchQueryCreate(BaseModel):
    query: str
    collection: str = "regulations"


class ResearchQueryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    query: str
    answer: str | None
    sources: list[dict]
    collection: str
    created_at: datetime
