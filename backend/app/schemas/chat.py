from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    collection: str = "policies"
    session_id: str | None = None


class ChatSource(BaseModel):
    citation: int
    document_id: str
    filename: str | None = None
    clause_number: str | None = None
    chunk_index: int | None = None
    score: float = 0.0
    snippet: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource] = []
