import uuid
from datetime import datetime, date

from sqlalchemy import String, Text, Date, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Regulation(Base):
    """A regulatory document tracked in the Regulation Repository (e.g. EU AI Act)."""

    __tablename__ = "regulations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(100), nullable=True)  # EU, US, UK, Global...
    category: Mapped[str] = mapped_column(String(100), nullable=True)  # AI Act, Data Privacy, Sector-specific...
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    source_url: Mapped[str] = mapped_column(String(500), nullable=True)
    effective_date: Mapped[date] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="tracked")  # tracked, in_force, proposed, repealed
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class RegulationClause(Base):
    """A granular article/section of a regulation, embedded into ChromaDB for retrieval."""

    __tablename__ = "regulation_clauses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    regulation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("regulations.id"))
    clause_number: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "Article 9"
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
