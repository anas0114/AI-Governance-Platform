"""Supervisor orchestration: routes a user message to the single best specialist agent."""
import operator
from typing import Annotated, Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, MessagesState, StateGraph
from pydantic import BaseModel

from app.agents.compliance_agent import compliance_agent
from app.agents.governance_advisor_agent import governance_advisor_agent
from app.agents.legal_research_agent import legal_research_agent
from app.agents.memory import get_memory_saver, thread_config
from app.agents.prompts import SUPERVISOR_PROMPT
from app.agents.risk_evaluation_agent import risk_evaluation_agent
from app.rag.chain import get_llm

SPECIALISTS = {
    "legal_research": legal_research_agent,
    "compliance": compliance_agent,
    "risk_evaluation": risk_evaluation_agent,
    "governance_advisor": governance_advisor_agent,
}


class RouteDecision(BaseModel):
    next: Literal["legal_research", "compliance", "risk_evaluation", "governance_advisor"]
    reason: str


class OrchestratorState(MessagesState):
    next: str
    agent_trace: Annotated[list[str], operator.add]


def supervisor_node(state: OrchestratorState) -> dict:
    messages = [SystemMessage(content=SUPERVISOR_PROMPT), *state["messages"]]
    decision = get_llm().with_structured_output(RouteDecision).invoke(messages)
    return {"next": decision.next if decision.next in SPECIALISTS else "governance_advisor"}


def _make_specialist_node(name: str):
    agent = SPECIALISTS[name]

    def node(state: OrchestratorState, config: RunnableConfig) -> dict:
        base_thread_id = config.get("configurable", {}).get("thread_id", "default")
        latest_question = next(m for m in reversed(state["messages"]) if isinstance(m, HumanMessage))
        # The specialist keeps its own per-session memory, so it only needs the new question.
        result = agent.invoke(
            {"messages": [latest_question]},
            config=thread_config(f"{base_thread_id}:{name}"),
        )
        last_message = result["messages"][-1]
        tagged = AIMessage(content=last_message.content, name=name)
        return {"messages": [tagged], "agent_trace": [name]}

    return node


def build_orchestrator_graph():
    """Builds the supervisor graph: supervisor -> exactly one specialist -> END."""
    graph = StateGraph(OrchestratorState)

    graph.add_node("supervisor", supervisor_node)
    for name in SPECIALISTS:
        graph.add_node(name, _make_specialist_node(name))
        graph.add_edge(name, END)

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges("supervisor", lambda state: state["next"], {name: name for name in SPECIALISTS})

    return graph.compile(checkpointer=get_memory_saver())


orchestrator_graph = build_orchestrator_graph()
