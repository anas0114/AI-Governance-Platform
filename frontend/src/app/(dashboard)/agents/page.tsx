"use client";

import { useState } from "react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { askAgent, getErrorMessage, orchestrateAgents } from "@/lib/api";
import type { AgentName } from "@/types/agent";

const AGENTS: { key: "legal-research" | "compliance" | "risk-evaluation" | "governance-advisor"; label: string; hint: string }[] = [
  { key: "legal-research", label: "Legal Research Agent", hint: "Ask about regulations, articles, legal obligations." },
  { key: "compliance", label: "Compliance Agent", hint: "Ask about framework/control compliance status." },
  { key: "risk-evaluation", label: "Risk Evaluation Agent", hint: "Ask to classify or look up AI system risk." },
  { key: "governance-advisor", label: "Governance Advisor Agent", hint: "Ask for policy-grounded recommendations." },
];

interface Exchange {
  query: string;
  answer: string;
  agent: string;
  trace?: AgentName[];
}

export default function AgentsPage() {
  const [selected, setSelected] = useState<(typeof AGENTS)[number]["key"] | "orchestrate">("orchestrate");
  const [query, setQuery] = useState("");
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const [history, setHistory] = useState<Exchange[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAsk(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    try {
      if (selected === "orchestrate") {
        const response = await orchestrateAgents(query, sessionId);
        setSessionId(response.session_id);
        setHistory((prev) => [
          ...prev,
          { query, answer: response.answer, agent: response.agent_trace.join(", ") || "orchestrator", trace: response.agent_trace },
        ]);
      } else {
        const response = await askAgent(selected, query, sessionId);
        setSessionId(response.session_id);
        setHistory((prev) => [...prev, { query, answer: response.answer, agent: response.agent }]);
      }
      setQuery("");
    } catch (err) {
      setError(getErrorMessage(err, "The agent request failed."));
    } finally {
      setLoading(false);
    }
  }

  function resetSession() {
    setSessionId(undefined);
    setHistory([]);
    setError(null);
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold text-slate-900">Governance Agents</h1>
      <p className="mt-2 text-slate-600">
        Four LangGraph specialist agents (Legal Research, Compliance, Risk Evaluation, Governance Advisor),
        coordinated by a supervisor orchestrator that routes each question automatically.
      </p>

      <Card className="mt-6">
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setSelected("orchestrate")}
            className={`rounded-full px-3 py-1 text-xs font-medium ${
              selected === "orchestrate" ? "bg-brand-600 text-white" : "bg-slate-100 text-slate-700"
            }`}
          >
            Auto-route (Orchestrator)
          </button>
          {AGENTS.map((agent) => (
            <button
              key={agent.key}
              onClick={() => setSelected(agent.key)}
              className={`rounded-full px-3 py-1 text-xs font-medium ${
                selected === agent.key ? "bg-brand-600 text-white" : "bg-slate-100 text-slate-700"
              }`}
            >
              {agent.label}
            </button>
          ))}
        </div>

        <form onSubmit={handleAsk} className="mt-4 flex gap-3">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. Is our credit scoring model compliant with the EU AI Act?"
            className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
          <Button type="submit" disabled={loading}>
            {loading ? "Thinking..." : "Ask"}
          </Button>
          <Button type="button" variant="secondary" onClick={resetSession}>
            New session
          </Button>
        </form>
        {error && (
          <p role="alert" className="mt-3 rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </p>
        )}

        <div className="mt-6 space-y-4">
          {history.map((exchange, i) => (
            <div key={i} className="rounded-md border border-slate-200 p-4">
              <p className="text-sm font-medium text-slate-900">{exchange.query}</p>
              <p className="mt-2 text-sm text-slate-600 whitespace-pre-wrap">{exchange.answer}</p>
              <p className="mt-2 text-xs text-slate-400">handled by: {exchange.agent}</p>
            </div>
          ))}
          {history.length === 0 && <p className="text-sm text-slate-500">No conversation yet.</p>}
        </div>
      </Card>
    </div>
  );
}
