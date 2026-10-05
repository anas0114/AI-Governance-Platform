import uuid

from fastapi import APIRouter, Depends
from starlette.concurrency import run_in_threadpool

from app.agents.compliance_agent import compliance_agent
from app.agents.governance_advisor_agent import governance_advisor_agent
from app.agents.legal_research_agent import legal_research_agent
from app.agents.memory import thread_config
from app.agents.orchestrator import orchestrator_graph
from app.agents.risk_evaluation_agent import risk_evaluation_agent
from app.api.deps import get_current_user, require_ai_configured
from app.schemas.agent import AgentQueryRequest, AgentQueryResponse, OrchestrationResponse

router = APIRouter(dependencies=[Depends(require_ai_configured)])

SPECIALIST_AGENTS = {
    "legal-research": ("legal_research", legal_research_agent),
    "compliance": ("compliance", compliance_agent),
    "risk-evaluation": ("risk_evaluation", risk_evaluation_agent),
    "governance-advisor": ("governance_advisor", governance_advisor_agent),
}


async def _invoke_specialist(agent_key: str, request: AgentQueryRequest) -> AgentQueryResponse:
    agent_name, agent = SPECIALIST_AGENTS[agent_key]
    session_id = request.session_id or str(uuid.uuid4())

    result = await run_in_threadpool(
        agent.invoke,
        {"messages": [("human", request.query)]},
        thread_config(f"{session_id}:{agent_name}"),
    )
    answer = result["messages"][-1].content
    return AgentQueryResponse(agent=agent_name, answer=answer, session_id=session_id)


@router.post("/legal-research", response_model=AgentQueryResponse)
async def legal_research(request: AgentQueryRequest, _=Depends(get_current_user)) -> AgentQueryResponse:
    """Legal Research Agent: researches regulations, articles, and legal obligations."""
    return await _invoke_specialist("legal-research", request)


@router.post("/compliance", response_model=AgentQueryResponse)
async def compliance(request: AgentQueryRequest, _=Depends(get_current_user)) -> AgentQueryResponse:
    """Compliance Agent: evaluates AI systems against tracked compliance frameworks/controls."""
    return await _invoke_specialist("compliance", request)


@router.post("/risk-evaluation", response_model=AgentQueryResponse)
async def risk_evaluation(request: AgentQueryRequest, _=Depends(get_current_user)) -> AgentQueryResponse:
    """Risk Evaluation Agent: classifies and reports on AI system risk levels."""
    return await _invoke_specialist("risk-evaluation", request)


@router.post("/governance-advisor", response_model=AgentQueryResponse)
async def governance_advisor(request: AgentQueryRequest, _=Depends(get_current_user)) -> AgentQueryResponse:
    """Governance Advisor Agent: synthesizes policy, risk, and compliance context into recommendations."""
    return await _invoke_specialist("governance-advisor", request)


@router.post("/orchestrate", response_model=OrchestrationResponse)
async def orchestrate(request: AgentQueryRequest, _=Depends(get_current_user)) -> OrchestrationResponse:
    """Supervisor orchestration: routes the query to the single best specialist agent."""
    session_id = request.session_id or str(uuid.uuid4())

    result = await run_in_threadpool(
        orchestrator_graph.invoke,
        {"messages": [("human", request.query)], "next": "", "agent_trace": []},
        thread_config(session_id),
    )

    answer = result["messages"][-1].content
    # agent_trace accumulates across the session's checkpoints; report only this turn's specialist.
    return OrchestrationResponse(answer=answer, session_id=session_id, agent_trace=result.get("agent_trace", [])[-1:])
