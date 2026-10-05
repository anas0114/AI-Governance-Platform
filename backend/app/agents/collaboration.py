"""Sequential multi-agent collaboration: Research -> Compliance -> Risk -> Governance.

Unlike the supervisor in orchestrator.py (which routes to a single best-matching
agent), this pipeline always runs all four specialists in a fixed order, each
building on the prior agents' findings, and produces one synthesized governance
recommendation with a full step-by-step trace for auditability.
"""
import operator
import time
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.compliance_agent import compliance_agent
from app.agents.governance_advisor_agent import governance_advisor_agent
from app.agents.legal_research_agent import legal_research_agent
from app.agents.memory import thread_config
from app.agents.observability import CollaborationTracer
from app.agents.risk_evaluation_agent import risk_evaluation_agent


class StepTrace(TypedDict):
    agent_name: str
    output: str
    duration_ms: float
    events: list[dict]


class CollaborationState(TypedDict):
    query: str
    session_id: str
    research_findings: str
    compliance_findings: str
    risk_findings: str
    governance_recommendation: str
    steps: Annotated[list[StepTrace], operator.add]


def _run_agent(agent, agent_name: str, prompt: str, session_id: str) -> StepTrace:
    """Invoke one specialist agent with tracing, returning its output plus observability events."""
    tracer = CollaborationTracer()
    started = time.perf_counter()

    result = agent.invoke(
        {"messages": [("human", prompt)]},
        config={
            **thread_config(f"{session_id}:collab:{agent_name}"),
            "callbacks": [tracer],
            "run_name": f"collaboration-{agent_name}",
            "tags": ["collaboration", agent_name],
        },
    )

    duration_ms = round((time.perf_counter() - started) * 1000, 1)
    output = result["messages"][-1].content
    return {"agent_name": agent_name, "output": output, "duration_ms": duration_ms, "events": tracer.events}


def research_node(state: CollaborationState) -> dict:
    prompt = (
        f"Research question: {state['query']}\n\n"
        "Identify the applicable regulations, articles, and policies, with citations."
    )
    step = _run_agent(legal_research_agent, "research", prompt, state["session_id"])
    return {"research_findings": step["output"], "steps": [step]}


def compliance_node(state: CollaborationState) -> dict:
    prompt = (
        f"Original question: {state['query']}\n\n"
        f"Legal research findings:\n{state['research_findings']}\n\n"
        "Using this context, evaluate compliance status against the relevant framework(s) and "
        "controls, and identify any gaps."
    )
    step = _run_agent(compliance_agent, "compliance", prompt, state["session_id"])
    return {"compliance_findings": step["output"], "steps": [step]}


def risk_node(state: CollaborationState) -> dict:
    prompt = (
        f"Original question: {state['query']}\n\n"
        f"Legal research findings:\n{state['research_findings']}\n\n"
        f"Compliance findings:\n{state['compliance_findings']}\n\n"
        "Using this context, assess the risk level, cite any open findings, and flag concerns."
    )
    step = _run_agent(risk_evaluation_agent, "risk_evaluation", prompt, state["session_id"])
    return {"risk_findings": step["output"], "steps": [step]}


def governance_node(state: CollaborationState) -> dict:
    prompt = (
        f"Original question: {state['query']}\n\n"
        f"Legal research findings:\n{state['research_findings']}\n\n"
        f"Compliance findings:\n{state['compliance_findings']}\n\n"
        f"Risk findings:\n{state['risk_findings']}\n\n"
        "Synthesize all of the above into one final governance recommendation with prioritized, "
        "actionable next steps."
    )
    step = _run_agent(governance_advisor_agent, "governance_advisor", prompt, state["session_id"])
    return {"governance_recommendation": step["output"], "steps": [step]}


def build_collaboration_graph():
    graph = StateGraph(CollaborationState)

    graph.add_node("research", research_node)
    graph.add_node("compliance", compliance_node)
    graph.add_node("risk_evaluation", risk_node)
    graph.add_node("governance_advisor", governance_node)

    graph.add_edge(START, "research")
    graph.add_edge("research", "compliance")
    graph.add_edge("compliance", "risk_evaluation")
    graph.add_edge("risk_evaluation", "governance_advisor")
    graph.add_edge("governance_advisor", END)

    return graph.compile()


collaboration_graph = build_collaboration_graph()
