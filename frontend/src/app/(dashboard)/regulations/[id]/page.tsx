"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { createRegulationClause, fetchRegulationClauses } from "@/lib/api";
import type { RegulationClause } from "@/types/regulation";

export default function RegulationDetailPage() {
  const params = useParams<{ id: string }>();
  const [clauses, setClauses] = useState<RegulationClause[]>([]);
  const [clauseNumber, setClauseNumber] = useState("");
  const [clauseTitle, setClauseTitle] = useState("");
  const [text, setText] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function load() {
    fetchRegulationClauses(params.id).then(setClauses);
  }

  useEffect(load, [params.id]);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!clauseNumber.trim() || !text.trim()) return;
    setSubmitting(true);
    try {
      await createRegulationClause(params.id, { clause_number: clauseNumber, title: clauseTitle, text });
      setClauseNumber("");
      setClauseTitle("");
      setText("");
      load();
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold text-slate-900">Regulation Clauses</h1>
      <p className="mt-2 text-slate-600">
        Clauses added here are automatically embedded into ChromaDB for the AI Copilot to cite.
      </p>

      <Card className="mt-6">
        <h2 className="font-medium text-slate-900">Add Clause</h2>
        <form onSubmit={handleCreate} className="mt-4 flex flex-col gap-3">
          <div className="flex gap-3">
            <input
              value={clauseNumber}
              onChange={(e) => setClauseNumber(e.target.value)}
              placeholder="Clause number (e.g. Article 9)"
              className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm"
            />
            <input
              value={clauseTitle}
              onChange={(e) => setClauseTitle(e.target.value)}
              placeholder="Title"
              className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm"
            />
          </div>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Clause text"
            rows={4}
            className="rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
          <Button type="submit" disabled={submitting} className="self-start">
            {submitting ? "Saving..." : "Add Clause"}
          </Button>
        </form>
      </Card>

      <div className="mt-6 space-y-4">
        {clauses.map((clause) => (
          <Card key={clause.id}>
            <h3 className="font-medium text-slate-900">
              {clause.clause_number} {clause.title && `— ${clause.title}`}
            </h3>
            <p className="mt-2 text-sm text-slate-600">{clause.text}</p>
          </Card>
        ))}
        {clauses.length === 0 && <p className="text-sm text-slate-500">No clauses added yet.</p>}
      </div>
    </div>
  );
}