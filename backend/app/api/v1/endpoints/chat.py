from fastapi import APIRouter, Depends
from starlette.concurrency import run_in_threadpool

from app.agents.graph import governance_graph
from app.api.deps import get_current_user, require_ai_configured
from app.schemas.chat import ChatRequest, ChatResponse, ChatSource

router = APIRouter(dependencies=[Depends(require_ai_configured)])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, _=Depends(get_current_user)) -> ChatResponse:
    """Run the LangGraph governance copilot workflow (retrieve -> classify risk -> generate answer)."""
    result = await run_in_threadpool(
        governance_graph.invoke,
        {
            "query": request.query,
            "collection": request.collection,
            "context": "",
            "retrieved_docs": [],
            "sources": [],
            "risk_level": None,
            "answer": "",
            "messages": [],
        }
    )
    sources = [ChatSource(**source) for source in result.get("sources", [])]
    return ChatResponse(answer=result["answer"], sources=sources)
