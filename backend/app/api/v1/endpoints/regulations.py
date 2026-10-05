import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.api.deps import get_current_user
from app.core.errors import is_openai_configured
from app.db.session import get_db
from app.models.regulation import Regulation, RegulationClause
from app.schemas.regulation import (
    RegulationClauseCreate,
    RegulationClauseRead,
    RegulationCreate,
    RegulationRead,
    RegulationUpdate,
)
from app.rag.ingestion import ingest_text

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=list[RegulationRead])
async def list_regulations(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)) -> list[Regulation]:
    result = await db.execute(select(Regulation).order_by(Regulation.title))
    return list(result.scalars().all())


@router.post("/", response_model=RegulationRead, status_code=status.HTTP_201_CREATED)
async def create_regulation(
    regulation_in: RegulationCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)
) -> Regulation:
    regulation = Regulation(**regulation_in.model_dump())
    db.add(regulation)
    await db.commit()
    await db.refresh(regulation)
    return regulation


@router.get("/{regulation_id}", response_model=RegulationRead)
async def get_regulation(
    regulation_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)
) -> Regulation:
    regulation = await db.get(Regulation, regulation_id)
    if not regulation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regulation not found")
    return regulation


@router.patch("/{regulation_id}", response_model=RegulationRead)
async def update_regulation(
    regulation_id: uuid.UUID,
    regulation_in: RegulationUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
) -> Regulation:
    regulation = await db.get(Regulation, regulation_id)
    if not regulation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regulation not found")
    for field, value in regulation_in.model_dump(exclude_unset=True).items():
        setattr(regulation, field, value)
    await db.commit()
    await db.refresh(regulation)
    return regulation


@router.delete("/{regulation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_regulation(
    regulation_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)
) -> None:
    regulation = await db.get(Regulation, regulation_id)
    if not regulation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regulation not found")
    await db.delete(regulation)
    await db.commit()


@router.get("/{regulation_id}/clauses", response_model=list[RegulationClauseRead])
async def list_clauses(
    regulation_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)
) -> list[RegulationClause]:
    result = await db.execute(
        select(RegulationClause).where(RegulationClause.regulation_id == regulation_id)
    )
    return list(result.scalars().all())


@router.post("/{regulation_id}/clauses", response_model=RegulationClauseRead, status_code=status.HTTP_201_CREATED)
async def create_clause(
    regulation_id: uuid.UUID,
    clause_in: RegulationClauseCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
) -> RegulationClause:
    """Create a regulation clause and embed its text into the ChromaDB regulations collection."""
    regulation = await db.get(Regulation, regulation_id)
    if not regulation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regulation not found")

    clause = RegulationClause(id=uuid.uuid4(), regulation_id=regulation_id, **clause_in.model_dump())

    # Index before committing so a failed embedding call never leaves an unsearchable clause behind.
    if is_openai_configured():
        await run_in_threadpool(
            ingest_text,
            "regulations",
            str(clause.id),
            f"{regulation.title} - {clause.clause_number} {clause.title or ''}\n{clause.text}",
            {"regulation_id": str(regulation_id), "clause_number": clause.clause_number},
        )
    else:
        logger.warning("OPENAI_API_KEY not configured; clause %s saved without search indexing", clause.id)

    db.add(clause)
    await db.commit()
    await db.refresh(clause)

    return clause
