"""Ingestion pipeline: load -> chunk -> embed -> store into ChromaDB."""
import uuid

from app.rag.chunking import chunk_text
from app.rag.loaders import load_text
from app.rag.vectorstore import delete_document_vectors, get_vectorstore


def ingest_text(collection: str, doc_id: str, text: str, metadata: dict | None = None) -> int:
    """Chunk raw text and embed it into the given collection. Returns the number of chunks stored."""
    base_metadata = {**(metadata or {}), "doc_id": doc_id}
    documents = chunk_text(text, metadata=base_metadata)
    if not documents:
        return 0

    delete_ingested_document(collection, doc_id)
    vectorstore = get_vectorstore(collection)
    ids = [f"{doc_id}-{doc.metadata['chunk_index']}" for doc in documents]
    vectorstore.add_documents(documents=documents, ids=ids)
    return len(documents)


def ingest_file(collection: str, filename: str, content: bytes, doc_id: str | None = None) -> tuple[str, int]:
    """Extract text from an uploaded file and ingest it. Returns (doc_id, chunk_count)."""
    doc_id = doc_id or str(uuid.uuid4())
    text = load_text(filename, content)
    chunk_count = ingest_text(collection, doc_id, text, metadata={"filename": filename})
    return doc_id, chunk_count


def delete_ingested_document(collection: str, doc_id: str) -> None:
    """Remove all embedded chunks for a document, e.g. when the document record is deleted."""
    delete_document_vectors(collection, doc_id)
