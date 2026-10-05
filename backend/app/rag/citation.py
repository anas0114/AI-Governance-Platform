"""Builds numbered citation markers ([1], [2], ...) and structured source metadata."""
from app.rag.retrieval import RetrievedChunk


def build_context_and_sources(chunks: list[RetrievedChunk]) -> tuple[str, list[dict]]:
    """Returns (context text with [n] markers, list of source dicts) aligned by index."""
    context_blocks: list[str] = []
    sources: list[dict] = []

    for i, chunk in enumerate(chunks, start=1):
        context_blocks.append(f"[{i}] {chunk.content}")
        sources.append(
            {
                "citation": i,
                "document_id": chunk.metadata.get("doc_id", "unknown"),
                "filename": chunk.metadata.get("filename"),
                "clause_number": chunk.metadata.get("clause_number"),
                "chunk_index": chunk.metadata.get("chunk_index"),
                "score": chunk.score,
                "snippet": chunk.content[:280],
            }
        )

    return "\n\n".join(context_blocks), sources
