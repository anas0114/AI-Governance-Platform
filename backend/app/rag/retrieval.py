"""Similarity-search retrieval over a ChromaDB collection with relevance scores."""
from dataclasses import dataclass, field

from app.rag.config import SCORE_THRESHOLD, TOP_K
from app.rag.vectorstore import get_vectorstore


@dataclass
class RetrievedChunk:
    content: str
    metadata: dict = field(default_factory=dict)
    score: float = 0.0


def retrieve(query: str, collection: str, k: int = TOP_K, score_threshold: float = SCORE_THRESHOLD) -> list[RetrievedChunk]:
    """Retrieve the top-k most relevant chunks for a query, filtered by a minimum relevance score."""
    vectorstore = get_vectorstore(collection)
    results = vectorstore.similarity_search_with_relevance_scores(query, k=k)

    return [
        RetrievedChunk(content=doc.page_content, metadata=doc.metadata, score=round(score, 4))
        for doc, score in results
        if score >= score_threshold
    ]
