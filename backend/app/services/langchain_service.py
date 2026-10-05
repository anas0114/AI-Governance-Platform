"""Deprecated: superseded by the app.rag package. Kept as a thin re-export for compatibility."""
from app.rag.chain import get_llm  # noqa: F401
from app.rag.chunking import chunk_text as _chunk_documents  # noqa: F401
from app.rag.embeddings import get_embeddings  # noqa: F401
from app.rag.ingestion import ingest_text as ingest_document  # noqa: F401
from app.rag.vectorstore import get_vectorstore  # noqa: F401


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 150) -> list[str]:
    return [doc.page_content for doc in _chunk_documents(text)]
