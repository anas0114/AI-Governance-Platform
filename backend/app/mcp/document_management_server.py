"""MCP server exposing Document Management: ingestion, search, listing, and deletion.

Run with:  python -m app.mcp.document_management_server
"""
import uuid

from mcp.server.fastmcp import FastMCP
from sqlalchemy import select

from app.db.sync_session import SyncSessionLocal
from app.mcp.common import parse_uuid
from app.models.document import Document
from app.rag.config import ALL_COLLECTIONS
from app.rag.ingestion import delete_ingested_document, ingest_text
from app.rag.retrieval import retrieve

mcp = FastMCP("document-management")


def _serialize(document: Document) -> dict:
    return {
        "id": str(document.id),
        "filename": document.filename,
        "collection": document.collection,
        "content_type": document.content_type,
        "chunk_count": document.chunk_count,
        "created_at": document.created_at.isoformat() if document.created_at else None,
    }


@mcp.tool()
def list_documents(collection: str | None = None) -> list[dict]:
    """List ingested documents, optionally filtered by collection (policies, regulations, evidence)."""
    with SyncSessionLocal() as db:
        query = select(Document)
        if collection:
            query = query.where(Document.collection == collection)
        documents = db.execute(query.order_by(Document.created_at.desc())).scalars().all()
    return [_serialize(d) for d in documents]


@mcp.tool()
def ingest_document_text(filename: str, collection: str, text: str) -> dict:
    """Ingest raw text as a document: chunk it, embed it into ChromaDB, and record it in the registry.

    Use this when a client has extracted document text but cannot upload the raw file bytes.
    """
    if collection not in ALL_COLLECTIONS:
        return {"error": f"Invalid collection '{collection}'. Must be one of {ALL_COLLECTIONS}."}

    document_id = uuid.uuid4()
    chunk_count = ingest_text(collection, str(document_id), text, metadata={"filename": filename})

    with SyncSessionLocal() as db:
        document = Document(
            id=document_id,
            filename=filename,
            storage_path=f"mcp-ingested/{document_id}-{filename}",
            collection=collection,
            content_type="text/plain",
            chunk_count=chunk_count,
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return _serialize(document)


@mcp.tool()
def search_documents(query: str, collection: str = "policies") -> list[dict]:
    """Run a similarity search over a document collection (policies, regulations, evidence)."""
    if collection not in ALL_COLLECTIONS:
        return [{"error": f"Invalid collection '{collection}'. Must be one of {ALL_COLLECTIONS}."}]

    chunks = retrieve(query, collection)
    return [{"content": c.content, "metadata": c.metadata, "score": c.score} for c in chunks]


@mcp.tool()
def get_document(document_id: str) -> dict:
    """Get metadata for a single ingested document by id."""
    with SyncSessionLocal() as db:
        document = db.get(Document, parse_uuid(document_id, "document_id"))
        if not document:
            return {"error": f"Document '{document_id}' not found."}
        return _serialize(document)


@mcp.tool()
def delete_document(document_id: str) -> dict:
    """Delete a document record and remove its embedded chunks from ChromaDB."""
    with SyncSessionLocal() as db:
        document = db.get(Document, parse_uuid(document_id, "document_id"))
        if not document:
            return {"error": f"Document '{document_id}' not found."}

        delete_ingested_document(document.collection, str(document.id))
        db.delete(document)
        db.commit()
        return {"id": document_id, "deleted": True}


if __name__ == "__main__":
    mcp.run()
