from typing import TypedDict, Annotated
import operator


class ChatSource(TypedDict, total=False):
    citation: int
    document_id: str
    filename: str | None
    clause_number: str | None
    chunk_index: int | None
    score: float
    snippet: str


class GovernanceAgentState(TypedDict):
    """Shared state passed between LangGraph nodes for the compliance copilot workflow."""

    query: str
    collection: str
    context: str
    retrieved_docs: list[str]
    sources: list[ChatSource]
    risk_level: str | None
    answer: str
    messages: Annotated[list[str], operator.add]
