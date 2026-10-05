"use client";

import { useEffect, useState } from "react";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { createPolicy, deletePolicy, fetchPolicies, updatePolicyStatus } from "@/lib/api";
import type { Policy } from "@/types/policy";
import { formatDate } from "@/lib/utils";

const statusStyles: Record<Policy["status"], string> = {
  draft: "bg-slate-100 text-slate-700",
  in_review: "bg-amber-100 text-amber-800",
  approved: "bg-emerald-100 text-emerald-800",
  retired: "bg-red-100 text-red-800",
};

export default function PoliciesPage() {
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function load() {
    fetchPolicies()
      .then(setPolicies)
      .catch(() => setError("Unable to load policies. Sign in and ensure the API is running."));
  }

  useEffect(load, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    setSubmitting(true);
    try {
      await createPolicy({ title, description });
      setTitle("");
      setDescription("");
      load();
    } finally {
      setSubmitting(false);
    }
  }

  async function handleStatusChange(id: string, status: Policy["status"]) {
    await updatePolicyStatus(id, status);
    load();
  }

  async function handleDelete(id: string) {
    await deletePolicy(id);
    load();
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold text-slate-900">Policy Management</h1>
      <p className="mt-2 text-slate-600">Manage governance policies and their approval workflow.</p>

      <Card className="mt-6">
        <h2 className="font-medium text-slate-900">New Policy</h2>
        <form onSubmit={handleCreate} className="mt-4 flex flex-col gap-3 sm:flex-row">
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Policy title"
            className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
          <input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Short description"
            className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
          <Button type="submit" disabled={submitting}>
            {submitting ? "Creating..." : "Create Policy"}
          </Button>
        </form>
      </Card>

      {error && <p className="mt-6 text-sm text-red-600">{error}</p>}

      <div className="mt-6 space-y-4">
        {policies.map((policy) => (
          <Card key={policy.id}>
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-medium text-slate-900">{policy.title}</h3>
                <p className="mt-1 text-sm text-slate-600">{policy.description}</p>
                <p className="mt-2 text-xs text-slate-400">
                  v{policy.version} · updated {formatDate(policy.updated_at)}
                </p>
              </div>
              <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${statusStyles[policy.status]}`}>
                {policy.status.replace("_", " ")}
              </span>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              <Button variant="secondary" onClick={() => handleStatusChange(policy.id, "in_review")}>
                Submit for Review
              </Button>
              <Button variant="secondary" onClick={() => handleStatusChange(policy.id, "approved")}>
                Approve
              </Button>
              <Button variant="secondary" onClick={() => handleStatusChange(policy.id, "retired")}>
                Retire
              </Button>
              <Button variant="secondary" onClick={() => handleDelete(policy.id)}>
                Delete
              </Button>
            </div>
          </Card>
        ))}
        {policies.length === 0 && !error && <p className="text-sm text-slate-500">No policies yet.</p>}
      </div>
    </div>
  );
}
