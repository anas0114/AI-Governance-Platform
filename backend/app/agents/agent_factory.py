"""Factory for building a single-agent LangGraph ReAct loop: agent <-> tools."""
from langchain_core.messages import SystemMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.agents.memory import get_memory_saver
from app.rag.chain import get_llm


def build_tool_agent(system_prompt: str, tools: list[BaseTool]):
    """Compile a small ReAct-style graph: agent node calls tools until it can answer directly."""
    llm_with_tools = get_llm().bind_tools(tools)

    def agent_node(state: MessagesState) -> dict:
        messages = state["messages"]
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=system_prompt), *messages]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")

    return graph.compile(checkpointer=get_memory_saver())
