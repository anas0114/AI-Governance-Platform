import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.agents.collaboration import collaboration_graph
from app.api.deps import get_current_user, require_ai_configured
from app.db.session import get_db
from app.models.collaboration import AgentCollaborationRun, AgentCollaborationStep
from app.schemas.collaboration import (
    CollaborationRequest,
    CollaborationResponse,
    CollaborationRunSummary,
    CollaborationStepRead,
)

router = APIRouter()


@router.post(
    "/",
    response_model=CollaborationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_ai_configured)],
)
async def run_collaboration(
    request: CollaborationRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> CollaborationResponse:
    """Run the Research -> Compliance -> Risk -> Governance multi-agent collaboration pipeline
    and persist the full step-by-step trace as an audit record."""
    session_id = request.session_id or str(uuid.uuid4())

    result = await run_in_threadpool(
        collaboration_graph.invoke,
        {
            "query": request.query,
            "session_id": session_id,
            "research_findings": "",
            "compliance_findings": "",
            "risk_findings": "",
            "governance_recommendation": "",
            "steps": [],
        },
        config={"run_name": "governance-collaboration", "tags": ["collaboration"]},
    )

    run = AgentCollaborationRun(
        query=request.query,
        session_id=session_id,
        final_recommendation=result["governance_recommendation"],
        requested_by=current_user.id,
    )
    db.add(run)
    await db.flush()

    for i, step in enumerate(result["steps"]):
        db.add(
            AgentCollaborationStep(
                run_id=run.id,
                step_order=i,
                agent_name=step["agent_name"],
                output=step["output"],
                events=step["events"],
                duration_ms=step["duration_ms"],
            )
        )

    await db.commit()
    await db.refresh(run)

    return CollaborationResponse(
        run_id=run.id,
        session_id=session_id,
        query=request.query,
        final_recommendation=run.final_recommendation or "",
        steps=[CollaborationStepRead(**step) for step in result["steps"]],
    )


@router.get("/", response_model=list[CollaborationRunSummary])
async def list_collaboration_runs(
    db: AsyncSession = Depends(get_db), _=Depends(get_current_user)
) -> list[AgentCollaborationRun]:
    """Audit trail: list past multi-agent collaboration runs, most recent first."""
    result = await db.execute(select(AgentCollaborationRun).order_by(AgentCollaborationRun.created_at.desc()))
    return list(result.scalars().all())


@router.get("/{run_id}", response_model=CollaborationResponse)
async def get_collaboration_run(
    run_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)
) -> CollaborationResponse:
    """Recommendation traceability: fetch the full per-agent trace for a past collaboration run."""
    run = await db.get(AgentCollaborationRun, run_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collaboration run not found")

    steps_result = await db.execute(
        select(AgentCollaborationStep)
        .where(AgentCollaborationStep.run_id == run_id)
        .order_by(AgentCollaborationStep.step_order)
    )
    steps = steps_result.scalars().all()

    return CollaborationResponse(
        run_id=run.id,
        session_id=run.session_id,
        query=run.query,
        final_recommendation=run.final_recommendation or "",
        steps=[
            CollaborationStepRead(
                agent_name=s.agent_name, output=s.output, duration_ms=s.duration_ms, events=s.events
            )
            for s in steps
        ],
    )
