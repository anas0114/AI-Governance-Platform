"""End-to-end RAG chain: retrieve grounded context, then generate a cited answer."""
from functools import lru_cache

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.rag.citation import build_context_and_sources
from app.rag.config import SCORE_THRESHOLD, TOP_K
from app.rag.retrieval import retrieve

RAG_SYSTEM_PROMPT = (
    "You are an AI governance and compliance assistant. Answer the user's question using ONLY "
    "the numbered context passages below. Every factual claim must include a citation marker "
    "like [1] or [2] referencing the passage it came from. If the context does not contain the "
    "answer, say you don't have enough information instead of guessing.\n\n"
    "Context:\n{context}"
)


@lru_cache
def get_llm(temperature: float = 0.0) -> ChatOpenAI:
    return ChatOpenAI(model=settings.OPENAI_MODEL, temperature=temperature, api_key=settings.OPENAI_API_KEY)


def answer_with_citations(
    query: str,
    collection: str,
    k: int = TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
) -> dict:
    """Retrieve relevant chunks and produce an LLM answer grounded in numbered citations.

    Returns: {"answer": str, "sources": list[dict]}
    """
    chunks = retrieve(query, collection, k=k, score_threshold=score_threshold)

    if not chunks:
        return {
            "answer": "I couldn't find any relevant information in the knowledge base to answer that.",
            "sources": [],
        }

    context, sources = build_context_and_sources(chunks)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", RAG_SYSTEM_PROMPT),
            ("human", "{question}"),
        ]
    )
    chain = prompt | get_llm()
    response = chain.invoke({"context": context, "question": query})

    return {"answer": response.content, "sources": sources}
