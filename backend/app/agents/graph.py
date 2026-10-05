from langgraph.graph import StateGraph, END

from app.agents.state import GovernanceAgentState
from app.agents.nodes import retrieve_node, classify_risk_node, generate_answer_node


def build_governance_graph():
    """Builds the LangGraph workflow: retrieve -> classify risk -> generate answer."""
    graph = StateGraph(GovernanceAgentState)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("classify_risk", classify_risk_node)
    graph.add_node("generate_answer", generate_answer_node)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "classify_risk")
    graph.add_edge("classify_risk", "generate_answer")
    graph.add_edge("generate_answer", END)

    return graph.compile()


governance_graph = build_governance_graph()
