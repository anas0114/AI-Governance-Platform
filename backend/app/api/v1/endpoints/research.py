import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.agents.graph import governance_graph
from app.api.deps import get_current_user, require_ai_configured
from app.db.session import get_db
from app.models.research import ResearchNote, ResearchQuery
from app.rag.config import ALL_COLLECTIONS
from app.schemas.research import (
    ResearchNoteCreate,
    ResearchNoteRead,
    ResearchNoteUpdate,
    ResearchQueryCreate,
    ResearchQueryRead,
)

router = APIRouter()


@router.get("/notes", response_model=list[ResearchNoteRead])
async def list_notes(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)) -> list[ResearchNote]:
    result = await db.execute(select(ResearchNote).order_by(ResearchNote.updated_at.desc()))
    return list(result.scalars().all())


@router.post("/notes", response_model=ResearchNoteRead, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_in: ResearchNoteCreate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
) -> ResearchNote:
    note = ResearchNote(**note_in.model_dump(), author_id=current_user.id)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


@router.patch("/notes/{note_id}", response_model=ResearchNoteRead)
async def update_note(
    note_id: uuid.UUID,
    note_in: ResearchNoteUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
) -> ResearchNote:
    note = await db.get(ResearchNote, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    for field, value in note_in.model_dump(exclude_unset=True).items():
        setattr(note, field, value)
    await db.commit()
    await db.refresh(note)
    return note


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)) -> None:
    note = await db.get(ResearchNote, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    await db.delete(note)
    await db.commit()


@router.get("/queries", response_model=list[ResearchQueryRead])
async def list_queries(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)) -> list[ResearchQuery]:
    result = await db.execute(select(ResearchQuery).order_by(ResearchQuery.created_at.desc()))
    return list(result.scalars().all())


@router.post(
    "/queries",
    response_model=ResearchQueryRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_ai_configured)],
)
async def run_query(
    query_in: ResearchQueryCreate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
) -> ResearchQuery:
    """Run the LangGraph copilot workflow over the given collection and persist the result."""
    if query_in.collection not in ALL_COLLECTIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid collection '{query_in.collection}'. Choose from: {', '.join(ALL_COLLECTIONS)}",
        )
    result = await run_in_threadpool(
        governance_graph.invoke,
        {
            "query": query_in.query,
            "collection": query_in.collection,
            "context": "",
            "retrieved_docs": [],
            "sources": [],
            "risk_level": None,
            "answer": "",
            "messages": [],
        }
    )

    research_query = ResearchQuery(
        query=query_in.query,
        answer=result["answer"],
        sources=result.get("sources", []),
        collection=query_in.collection,
        author_id=current_user.id,
    )
    db.add(research_query)
    await db.commit()
    await db.refresh(research_query)
    return research_query
