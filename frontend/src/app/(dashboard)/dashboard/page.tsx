"use client";

import { useEffect, useState } from "react";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import { fetchDashboardSummary } from "@/lib/api";
import type { ComplianceDashboardSummary } from "@/types/dashboard";

export default function DashboardPage() {
  const [summary, setSummary] = useState<ComplianceDashboardSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardSummary()
      .then(setSummary)
      .catch(() => setError("Unable to load dashboard data. Sign in and ensure the API is running."));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-semibold text-slate-900">Compliance Dashboard</h1>
      <p className="mt-2 text-slate-600">
        A real-time view of AI system risk, policy status, assessments, and open audit findings.
      </p>

      {error && <p className="mt-6 text-sm text-red-600">{error}</p>}

      {summary && (
        <>
          <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Card>
              <p className="text-sm text-slate-500">AI Systems</p>
              <p className="mt-1 text-3xl font-semibold text-slate-900">{summary.total_ai_systems}</p>
            </Card>
            <Card>
              <p className="text-sm text-slate-500">Policies</p>
              <p className="mt-1 text-3xl font-semibold text-slate-900">{summary.total_policies}</p>
            </Card>
            <Card>
              <p className="text-sm text-slate-500">Audits</p>
              <p className="mt-1 text-3xl font-semibold text-slate-900">{summary.total_audits}</p>
            </Card>
            <Card>
              <p className="text-sm text-slate-500">Avg. Compliance Score</p>
              <p className="mt-1 text-3xl font-semibold text-slate-900">{summary.average_compliance_score}%</p>
            </Card>
          </div>

          <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-3">
            <Card>
              <h2 className="font-medium text-slate-900">AI System Risk Levels</h2>
              <div className="mt-4 space-y-2">
                {Object.entries(summary.risk_breakdown).map(([level, count]) => (
                  <div key={level} className="flex items-center justify-between text-sm">
                    <Badge level={level}>{level}</Badge>
                    <span className="font-medium text-slate-700">{count}</span>
                  </div>
                ))}
              </div>
            </Card>
            <Card>
              <h2 className="font-medium text-slate-900">Assessment Status</h2>
              <div className="mt-4 space-y-2 text-sm">
                {Object.entries(summary.assessment_breakdown).map(([status, count]) => (
                  <div key={status} className="flex items-center justify-between">
                    <span className="capitalize text-slate-600">{status.replace("_", " ")}</span>
                    <span className="font-medium text-slate-700">{count}</span>
                  </div>
                ))}
              </div>
            </Card>
            <Card>
              <h2 className="font-medium text-slate-900">Policy Status</h2>
              <div className="mt-4 space-y-2 text-sm">
                {Object.entries(summary.policy_breakdown).map(([status, count]) => (
                  <div key={status} className="flex items-center justify-between">
                    <span className="capitalize text-slate-600">{status.replace("_", " ")}</span>
                    <span className="font-medium text-slate-700">{count}</span>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          <Card className="mt-6">
            <p className="text-sm text-slate-500">Open Audit Findings</p>
            <p className="mt-1 text-2xl font-semibold text-red-600">{summary.open_findings}</p>
          </Card>
        </>
      )}
    </div>
  );
}
