"use client";

import { useEffect, useState } from "react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { fetchCollaborationRun, fetchCollaborationRuns, getErrorMessage, runCollaboration } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import type { CollaborationResponse, CollaborationRunSummary } from "@/types/collaboration";

const STAGE_LABELS: Record<string, string> = {
  research: "Research Agent",
  compliance: "Compliance Agent",
  risk_evaluation: "Risk Agent",
  governance_advisor: "Governance Agent",
};

export default function CollaborationPage() {
  const [query, setQuery] = useState("");
  const [running, setRunning] = useState(false);
  const [current, setCurrent] = useState<CollaborationResponse | null>(null);
  const [runs, setRuns] = useState<CollaborationRunSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [runError, setRunError] = useState<string | null>(null);

  function loadRuns() {
    fetchCollaborationRuns()
      .then(setRuns)
      .catch((err) => setError(getErrorMessage(err, "Unable to load audit trail.")));
  }

  useEffect(loadRuns, []);

  async function handleRun(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setRunning(true);
    setRunError(null);
    try {
      const result = await runCollaboration(query);
      setCurrent(result);
      setQuery("");
      loadRuns();
    } catch (err) {
      setRunError(getErrorMessage(err, "The collaboration run failed."));
    } finally {
      setRunning(false);
    }
  }

  async function handleViewRun(runId: string) {
    setRunError(null);
    try {
      setCurrent(await fetchCollaborationRun(runId));
    } catch (err) {
      setRunError(getErrorMessage(err, "Could not load that run."));
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold text-slate-900">Multi-Agent Collaboration</h1>
      <p className="mt-2 text-slate-600">
        Runs the full pipeline — Research Agent → Compliance Agent → Risk Agent → Governance Agent — and
        records a traceable audit trail of every step, tool call, and recommendation.
      </p>

      <Card className="mt-6">
        <form onSubmit={handleRun} className="flex gap-3">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. Should we deploy our resume screening model in the EU?"
            className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
          <Button type="submit" disabled={running}>
            {running ? "Running pipeline..." : "Run Collaboration"}
          </Button>
        </form>
        {running && (
          <p className="mt-3 text-sm text-slate-500">
            Four agents run in sequence; this can take a minute or two.
          </p>
        )}
        {runError && (
          <p role="alert" className="mt-3 rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">
            {runError}
          </p>
        )}
      </Card>

      {current && (
        <Card className="mt-6">
          <p className="text-sm font-medium text-slate-900">{current.query}</p>

          <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-slate-500">
            {current.steps.map((step, i) => (
              <span key={step.agent_name} className="flex items-center gap-2">
                <span className="rounded-full bg-brand-100 px-2.5 py-1 font-medium text-brand-700">
                  {STAGE_LABELS[step.agent_name] ?? step.agent_name}
                  {step.duration_ms != null && ` (${Math.round(step.duration_ms)}ms)`}
                </span>
                {i < current.steps.length - 1 && <span>→</span>}
              </span>
            ))}
          </div>

          <div className="mt-4 rounded-md bg-slate-50 p-4">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Final Recommendation</p>
            <p className="mt-2 whitespace-pre-wrap text-sm text-slate-800">{current.final_recommendation}</p>
          </div>

          <div className="mt-4 space-y-3">
            {current.steps.map((step) => (
              <details key={step.agent_name} className="rounded-md border border-slate-200 p-3">
                <summary className="cursor-pointer text-sm font-medium text-slate-900">
                  {STAGE_LABELS[step.agent_name] ?? step.agent_name} output & trace ({step.events.length} events)
                </summary>
                <p className="mt-2 whitespace-pre-wrap text-sm text-slate-600">{step.output}</p>
                <div className="mt-3 space-y-1 border-t border-slate-100 pt-2">
                  {step.events.map((event, i) => (
                    <p key={i} className="font-mono text-xs text-slate-400">
                      [{event.phase}] {event.type}:{event.name}
                      {event.duration_ms != null ? ` (${event.duration_ms}ms)` : ""}
                    </p>
                  ))}
                </div>
              </details>
            ))}
          </div>
        </Card>
      )}

      <Card className="mt-6">
        <h2 className="font-medium text-slate-900">Audit Trail</h2>
        {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
        <div className="mt-4 space-y-2">
          {runs.map((run) => (
            <button
              key={run.id}
              onClick={() => handleViewRun(run.id)}
              className="block w-full rounded-md border border-slate-200 p-3 text-left hover:bg-slate-50"
            >
              <p className="text-sm font-medium text-slate-900">{run.query}</p>
              <p className="mt-1 text-xs text-slate-400">{formatDate(run.created_at)} · session {run.session_id}</p>
            </button>
          ))}
          {runs.length === 0 && !error && <p className="text-sm text-slate-500">No collaboration runs yet.</p>}
        </div>
      </Card>
    </div>
  );
}
