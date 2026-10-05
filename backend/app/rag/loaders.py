"""Document loaders that turn raw uploaded bytes into plain text for chunking.

Supports .txt/.md (utf-8), .pdf (pypdf), and .docx (docx2txt). Falls back to a
best-effort utf-8 decode for unrecognized types.
"""
import io
from pathlib import Path


def _load_pdf(content: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(content))
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)


def _load_docx(content: bytes) -> str:
    import docx2txt

    with io.BytesIO(content) as buffer:
        return docx2txt.process(buffer) or ""


def _load_plain_text(content: bytes) -> str:
    return content.decode("utf-8", errors="ignore")


def load_text(filename: str, content: bytes) -> str:
    """Extract plain text from raw file bytes based on the file extension."""
    extension = Path(filename).suffix.lower()

    if extension == ".pdf":
        return _load_pdf(content)
    if extension == ".docx":
        return _load_docx(content)
    return _load_plain_text(content)
