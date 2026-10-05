"use client";

import { useEffect, useState } from "react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import {
  createResearchNote,
  deleteResearchNote,
  fetchResearchNotes,
  fetchResearchQueries,
  getErrorMessage,
  runResearchQuery,
} from "@/lib/api";
import type { ResearchNote, ResearchQuery } from "@/types/research";

export default function ResearchWorkspacePage() {
  const [notes, setNotes] = useState<ResearchNote[]>([]);
  const [queries, setQueries] = useState<ResearchQuery[]>([]);
  const [query, setQuery] = useState("");
  const [asking, setAsking] = useState(false);
  const [noteTitle, setNoteTitle] = useState("");
  const [noteContent, setNoteContent] = useState("");
  const [savingNote, setSavingNote] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function loadNotes() {
    fetchResearchNotes()
      .then(setNotes)
      .catch((err) => setError(getErrorMessage(err, "Unable to load notes.")));
  }

  function loadQueries() {
    fetchResearchQueries()
      .then(setQueries)
      .catch((err) => setError(getErrorMessage(err, "Unable to load research history.")));
  }

  useEffect(() => {
    loadNotes();
    loadQueries();
  }, []);

  async function handleAsk(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setAsking(true);
    setError(null);
    try {
      await runResearchQuery(query, "regulations");
      setQuery("");
      loadQueries();
    } catch (err) {
      setError(getErrorMessage(err, "The research query failed."));
    } finally {
      setAsking(false);
    }
  }

  async function handleSaveNote(e: React.FormEvent) {
    e.preventDefault();
    if (!noteTitle.trim() || !noteContent.trim()) return;
    setSavingNote(true);
    setError(null);
    try {
      await createResearchNote({ title: noteTitle, content: noteContent });
      setNoteTitle("");
      setNoteContent("");
      loadNotes();
    } catch (err) {
      setError(getErrorMessage(err, "Could not save the note."));
    } finally {
      setSavingNote(false);
    }
  }

  async function handleDeleteNote(id: string) {
    try {
      await deleteResearchNote(id);
      loadNotes();
    } catch (err) {
      setError(getErrorMessage(err, "Could not delete the note."));
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold text-slate-900">Research Workspace</h1>
      <p className="mt-2 text-slate-600">
        Ask grounded questions across regulations and policies, then capture findings as notes.
      </p>
      {error && (
        <p role="alert" className="mt-4 rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </p>
      )}

      <Card className="mt-6">
        <h2 className="font-medium text-slate-900">Ask the Copilot</h2>
        <form onSubmit={handleAsk} className="mt-4 flex gap-3">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. What are the transparency obligations under the EU AI Act?"
            className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
          <Button type="submit" disabled={asking}>
            {asking ? "Researching..." : "Ask"}
          </Button>
        </form>

        <div className="mt-6 space-y-4">
          {queries.map((q) => (
            <div key={q.id} className="rounded-md border border-slate-200 p-4">
              <p className="text-sm font-medium text-slate-900">{q.query}</p>
              <p className="mt-2 text-sm text-slate-600">{q.answer}</p>
              {q.sources.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {q.sources.map((source) => (
                    <span
                      key={source.citation}
                      title={source.snippet}
                      className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-500"
                    >
                      [{source.citation}] {source.filename ?? source.clause_number ?? source.document_id}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
          {queries.length === 0 && <p className="text-sm text-slate-500">No research queries yet.</p>}
        </div>
      </Card>

      <Card className="mt-6">
        <h2 className="font-medium text-slate-900">Notes</h2>
        <form onSubmit={handleSaveNote} className="mt-4 flex flex-col gap-3">
          <input
            value={noteTitle}
            onChange={(e) => setNoteTitle(e.target.value)}
            placeholder="Note title"
            className="rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
          <textarea
            value={noteContent}
            onChange={(e) => setNoteContent(e.target.value)}
            placeholder="Findings, summaries, mappings..."
            rows={3}
            className="rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
          <Button type="submit" disabled={savingNote} className="self-start">
            {savingNote ? "Saving..." : "Save Note"}
          </Button>
        </form>

        <div className="mt-6 space-y-3">
          {notes.map((note) => (
            <div key={note.id} className="rounded-md border border-slate-200 p-4">
              <div className="flex items-start justify-between">
                <h3 className="font-medium text-slate-900">{note.title}</h3>
                <Button variant="secondary" onClick={() => handleDeleteNote(note.id)}>
                  Delete
                </Button>
              </div>
              <p className="mt-2 text-sm text-slate-600">{note.content}</p>
            </div>
          ))}
          {notes.length === 0 && <p className="text-sm text-slate-500">No notes saved yet.</p>}
        </div>
      </Card>
    </div>
  );
}