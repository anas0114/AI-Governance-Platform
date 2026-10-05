import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.api.deps import get_current_user
from app.core.errors import is_openai_configured
from app.db.session import get_db
from app.models.policy import Policy
from app.rag.ingestion import ingest_text
from app.schemas.policy import PolicyCreate, PolicyRead, PolicyUpdate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=list[PolicyRead])
async def list_policies(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)) -> list[Policy]:
    result = await db.execute(select(Policy))
    return list(result.scalars().all())


@router.post("/", response_model=PolicyRead, status_code=status.HTTP_201_CREATED)
async def create_policy(
    policy_in: PolicyCreate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
) -> Policy:
    policy = Policy(**policy_in.model_dump(), owner_id=current_user.id)
    db.add(policy)
    await db.commit()
    await db.refresh(policy)
    if policy.content and is_openai_configured():
        await run_in_threadpool(
            ingest_text,
            "governance_documents",
            str(policy.id),
            f"{policy.title}\n{policy.content}",
            {"filename": policy.title, "policy_id": str(policy.id)},
        )
    return policy


@router.get("/{policy_id}", response_model=PolicyRead)
async def get_policy(policy_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)) -> Policy:
    policy = await db.get(Policy, policy_id)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
    return policy


@router.patch("/{policy_id}", response_model=PolicyRead)
async def update_policy(
    policy_id: uuid.UUID,
    policy_in: PolicyUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
) -> Policy:
    policy = await db.get(Policy, policy_id)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
    for field, value in policy_in.model_dump(exclude_unset=True).items():
        setattr(policy, field, value)
    await db.commit()
    await db.refresh(policy)
    if policy.content and is_openai_configured():
        await run_in_threadpool(
            ingest_text,
            "governance_documents",
            str(policy.id),
            f"{policy.title}\n{policy.content}",
            {"filename": policy.title, "policy_id": str(policy.id)},
        )
    return policy


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(policy_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)) -> None:
    policy = await db.get(Policy, policy_id)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")
    await db.delete(policy)
    await db.commit()
