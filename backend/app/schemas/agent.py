from pydantic import BaseModel


class AgentQueryRequest(BaseModel):
    query: str
    session_id: str | None = None


class AgentQueryResponse(BaseModel):
    agent: str
    answer: str
    session_id: str


class OrchestrationResponse(BaseModel):
    answer: str
    session_id: str
    agent_trace: list[str]
