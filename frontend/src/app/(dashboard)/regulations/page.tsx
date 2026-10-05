"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { createRegulation, fetchRegulations } from "@/lib/api";
import type { Regulation } from "@/types/regulation";

export default function RegulationsPage() {
  const [regulations, setRegulations] = useState<Regulation[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [jurisdiction, setJurisdiction] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function load() {
    fetchRegulations()
      .then(setRegulations)
      .catch(() => setError("Unable to load regulations. Sign in and ensure the API is running."));
  }

  useEffect(load, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    setSubmitting(true);
    try {
      await createRegulation({ title, jurisdiction });
      setTitle("");
      setJurisdiction("");
      load();
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold text-slate-900">Regulation Repository</h1>
      <p className="mt-2 text-slate-600">
        Track applicable AI regulations and drill into individual articles/clauses embedded for the copilot.
      </p>

      <Card className="mt-6">
        <h2 className="font-medium text-slate-900">Add Regulation</h2>
        <form onSubmit={handleCreate} className="mt-4 flex flex-col gap-3 sm:flex-row">
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Regulation title"
            className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
          <input
            value={jurisdiction}
            onChange={(e) => setJurisdiction(e.target.value)}
            placeholder="Jurisdiction (e.g. EU)"
            className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
          <Button type="submit" disabled={submitting}>
            {submitting ? "Adding..." : "Add Regulation"}
          </Button>
        </form>
      </Card>

      {error && <p className="mt-6 text-sm text-red-600">{error}</p>}

      <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2">
        {regulations.map((regulation) => (
          <Link key={regulation.id} href={`/regulations/${regulation.id}`}>
            <Card className="h-full transition-shadow hover:shadow-md">
              <div className="flex items-center justify-between">
                <h3 className="font-medium text-slate-900">{regulation.title}</h3>
                <span className="rounded-full bg-brand-100 px-2.5 py-0.5 text-xs font-medium text-brand-700">
                  {regulation.status}
                </span>
              </div>
              <p className="mt-2 text-sm text-slate-500">
                {regulation.jurisdiction} {regulation.category ? `· ${regulation.category}` : ""}
              </p>
              <p className="mt-2 text-sm text-slate-600 line-clamp-3">{regulation.summary}</p>
            </Card>
          </Link>
        ))}
        {regulations.length === 0 && !error && <p className="text-sm text-slate-500">No regulations tracked yet.</p>}
      </div>
    </div>
  );
}