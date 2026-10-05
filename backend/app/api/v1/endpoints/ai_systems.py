import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.ai_system import AISystem
from app.schemas.ai_system import AISystemCreate, AISystemRead

router = APIRouter()


@router.get("/", response_model=list[AISystemRead])
async def list_ai_systems(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)) -> list[AISystem]:
    result = await db.execute(select(AISystem))
    return list(result.scalars().all())


@router.post("/", response_model=AISystemRead, status_code=status.HTTP_201_CREATED)
async def create_ai_system(
    system_in: AISystemCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)
) -> AISystem:
    system = AISystem(**system_in.model_dump())
    db.add(system)
    await db.commit()
    await db.refresh(system)
    return system


@router.get("/{system_id}", response_model=AISystemRead)
async def get_ai_system(system_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)) -> AISystem:
    system = await db.get(AISystem, system_id)
    if not system:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI system not found")
    return system
