"use client";

import { useEffect, useState } from "react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { deleteDocument, fetchDocuments, getErrorMessage, uploadDocument } from "@/lib/api";
import type { DocumentRecord } from "@/types/document";
import { formatDate } from "@/lib/utils";

const COLLECTIONS = [
  { value: "regulations", label: "Regulations" },
  { value: "industry_standards", label: "Industry Standards" },
  { value: "audit_findings", label: "Audit Findings" },
  { value: "governance_documents", label: "Governance Documents" },
  { value: "policies", label: "Policies (legacy)" },
  { value: "evidence", label: "Evidence (legacy)" },
];

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [collection, setCollection] = useState(COLLECTIONS[0].value);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  function load() {
    fetchDocuments()
      .then(setDocuments)
      .catch((err) => setError(getErrorMessage(err, "Unable to load documents.")));
  }

  useEffect(load, []);

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      await uploadDocument(file, collection);
      setFile(null);
      load();
    } catch (err) {
      setError(getErrorMessage(err, "Upload failed."));
    } finally {
      setUploading(false);
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteDocument(id);
      load();
    } catch (err) {
      setError(getErrorMessage(err, "Could not delete the document."));
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold text-slate-900">Document Ingestion</h1>
      <p className="mt-2 text-slate-600">
        Upload policies, regulations, or evidence (.txt, .md, .pdf, .docx). Files are chunked, embedded, and
        stored in ChromaDB for retrieval by the AI Copilot and Research Workspace.
      </p>

      <Card className="mt-6">
        <h2 className="font-medium text-slate-900">Upload Document</h2>
        <form onSubmit={handleUpload} className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center">
          <select
            value={collection}
            onChange={(e) => setCollection(e.target.value)}
            className="rounded-md border border-slate-300 px-3 py-2 text-sm"
          >
            {COLLECTIONS.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>
          <input
            type="file"
            accept=".txt,.md,.pdf,.docx"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
          <Button type="submit" disabled={uploading || !file}>
            {uploading ? "Uploading..." : "Upload & Ingest"}
          </Button>
        </form>
      </Card>

      {error && <p className="mt-6 text-sm text-red-600">{error}</p>}

      <div className="mt-6 space-y-3">
        {documents.map((doc) => (
          <Card key={doc.id} className="flex items-center justify-between">
            <div>
              <p className="font-medium text-slate-900">{doc.filename}</p>
              <p className="mt-1 text-xs text-slate-500">
                {doc.collection} · {doc.chunk_count} chunks · uploaded {formatDate(doc.created_at)}
              </p>
            </div>
            <Button variant="secondary" onClick={() => handleDelete(doc.id)}>
              Delete
            </Button>
          </Card>
        ))}
        {documents.length === 0 && !error && <p className="text-sm text-slate-500">No documents uploaded yet.</p>}
      </div>
    </div>
  );
}
