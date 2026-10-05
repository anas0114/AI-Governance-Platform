import os
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.api.deps import get_current_user, require_ai_configured
from app.db.session import get_db
from app.models.document import Document
from app.rag.config import ALL_COLLECTIONS, SUPPORTED_EXTENSIONS
from app.rag.ingestion import delete_ingested_document, ingest_file
from app.rag.retrieval import retrieve
from app.schemas.document import DocumentRead

router = APIRouter()

UPLOAD_DIR = "uploads"


@router.get("/", response_model=list[DocumentRead])
async def list_documents(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)) -> list[Document]:
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    return list(result.scalars().all())


@router.post(
    "/upload",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_ai_configured)],
)
async def upload_document(
    file: UploadFile = File(...),
    collection: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Document:
    """Upload a document, persist its metadata, and run it through the RAG ingestion pipeline
    (load -> chunk -> embed -> store in ChromaDB)."""
    if collection not in ALL_COLLECTIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid collection '{collection}'. Must be one of: {', '.join(ALL_COLLECTIONS)}",
        )

    # Strip any client-supplied directory components to prevent path traversal.
    filename = os.path.basename((file.filename or "").replace("\\", "/"))
    extension = os.path.splitext(filename)[1].lower()
    if not filename or extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{extension}'. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
        )

    content_bytes = await file.read()
    document_id = uuid.uuid4()
    doc_id = str(document_id)

    _, chunk_count = await run_in_threadpool(ingest_file, collection, filename, content_bytes, doc_id=doc_id)
    if chunk_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No readable text was found in this file.",
        )

    document = Document(
        id=document_id,
        filename=filename,
        storage_path=os.path.join(UPLOAD_DIR, f"{doc_id}{extension}"),
        collection=collection,
        content_type=file.content_type,
        chunk_count=chunk_count,
        uploaded_by=current_user.id,
    )

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(document.storage_path, "wb") as f:
        f.write(content_bytes)

    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document


@router.get("/{document_id}", response_model=DocumentRead)
async def get_document(
    document_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)
) -> Document:
    document = await db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)
) -> None:
    """Delete the document record and remove its embedded chunks from ChromaDB."""
    document = await db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    delete_ingested_document(document.collection, str(document.id))
    if os.path.exists(document.storage_path):
        os.remove(document.storage_path)

    await db.delete(document)
    await db.commit()


@router.get("/{document_id}/search")
async def search_document_chunks(
    document_id: uuid.UUID,
    q: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
) -> list[dict]:
    """Debug endpoint: run a similarity search scoped to a document's collection."""
    document = await db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    chunks = retrieve(q, document.collection)
    return [{"content": c.content, "metadata": c.metadata, "score": c.score} for c in chunks]
