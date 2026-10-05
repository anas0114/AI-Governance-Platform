from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.api.deps import get_current_user
from app.core.errors import is_openai_configured
from app.db.session import get_db
from app.models.audit import Audit, AuditFinding
from app.rag.ingestion import ingest_text
from app.schemas.audit import AuditCreate, AuditFindingCreate, AuditFindingRead, AuditRead

router = APIRouter()


@router.get("/", response_model=list[AuditRead])
async def list_audits(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)) -> list[Audit]:
    result = await db.execute(select(Audit))
    return list(result.scalars().all())


@router.post("/", response_model=AuditRead, status_code=status.HTTP_201_CREATED)
async def create_audit(
    audit_in: AuditCreate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
) -> Audit:
    audit = Audit(**audit_in.model_dump(), auditor_id=current_user.id)
    db.add(audit)
    await db.commit()
    await db.refresh(audit)
    return audit


@router.post("/findings", response_model=AuditFindingRead, status_code=status.HTTP_201_CREATED)
async def create_finding(
    finding_in: AuditFindingCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)
) -> AuditFinding:
    finding = AuditFinding(**finding_in.model_dump())
    db.add(finding)
    await db.commit()
    await db.refresh(finding)
    if is_openai_configured():
        await run_in_threadpool(
            ingest_text,
            "audit_findings",
            str(finding.id),
            f"{finding.severity.upper()} finding\n{finding.description}\nRemediation: {finding.remediation or 'Not provided'}",
            {"filename": f"audit-finding-{finding.id}", "audit_id": str(finding.audit_id)},
        )
    return finding
