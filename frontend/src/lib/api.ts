import axios, { isAxiosError } from "axios";
import { clearSession, getValidToken, redirectToLogin } from "@/lib/auth";
import type { ChatResponse } from "@/types/chat";
import type { AuthUser } from "@/types/auth";
import type { Policy } from "@/types/policy";
import type { Regulation, RegulationClause } from "@/types/regulation";
import type { ResearchNote, ResearchQuery } from "@/types/research";
import type { ComplianceDashboardSummary } from "@/types/dashboard";
import type { AISystem } from "@/types/ai-system";
import type { DocumentRecord } from "@/types/document";
import type { AgentQueryResponse, OrchestrationResponse } from "@/types/agent";
import type { CollaborationResponse, CollaborationRunSummary } from "@/types/collaboration";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

export function getErrorMessage(err: unknown, fallback = "Something went wrong. Please try again."): string {
  if (isAxiosError(err)) {
    if (!err.response) return "Cannot reach the API server. Make sure the backend is running on port 8000.";
    const detail = (err.response.data as { detail?: unknown } | undefined)?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) return detail.map((d: { msg?: string }) => d.msg ?? "").filter(Boolean).join("; ");
  }
  return fallback;
}

apiClient.interceptors.request.use((config) => {
  const token = getValidToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const isLoginRequest = error.config?.url?.includes("/auth/login");
    if (error.response?.status === 401 && !isLoginRequest) {
      clearSession();
      redirectToLogin();
    }
    return Promise.reject(error);
  }
);

export async function login(email: string, password: string): Promise<string> {
  const form = new URLSearchParams();
  form.set("username", email);
  form.set("password", password);
  const { data } = await apiClient.post<{ access_token: string }>("/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return data.access_token;
}

export async function fetchCurrentUser(): Promise<AuthUser> {
  const { data } = await apiClient.get<AuthUser>("/users/me");
  return data;
}

export async function registerUser(payload: { email: string; password: string; full_name?: string }): Promise<AuthUser> {
  const { data } = await apiClient.post<AuthUser>("/auth/register", payload);
  return data;
}

export async function sendChatMessage(query: string): Promise<ChatResponse> {
  const { data } = await apiClient.post<ChatResponse>("/chat/", { query });
  return data;
}

export async function fetchPolicies(): Promise<Policy[]> {
  const { data } = await apiClient.get<Policy[]>("/policies/");
  return data;
}

export async function createPolicy(payload: { title: string; description?: string; content?: string }): Promise<Policy> {
  const { data } = await apiClient.post<Policy>("/policies/", payload);
  return data;
}

export async function updatePolicyStatus(id: string, status: Policy["status"]): Promise<Policy> {
  const { data } = await apiClient.patch<Policy>(`/policies/${id}`, { status });
  return data;
}

export async function deletePolicy(id: string): Promise<void> {
  await apiClient.delete(`/policies/${id}`);
}

export async function fetchRegulations(): Promise<Regulation[]> {
  const { data } = await apiClient.get<Regulation[]>("/regulations/");
  return data;
}

export async function createRegulation(payload: Partial<Regulation>): Promise<Regulation> {
  const { data } = await apiClient.post<Regulation>("/regulations/", payload);
  return data;
}

export async function fetchRegulationClauses(regulationId: string): Promise<RegulationClause[]> {
  const { data } = await apiClient.get<RegulationClause[]>(`/regulations/${regulationId}/clauses`);
  return data;
}

export async function createRegulationClause(
  regulationId: string,
  payload: { clause_number: string; title?: string; text: string }
): Promise<RegulationClause> {
  const { data } = await apiClient.post<RegulationClause>(`/regulations/${regulationId}/clauses`, payload);
  return data;
}

export async function fetchDashboardSummary(): Promise<ComplianceDashboardSummary> {
  const { data } = await apiClient.get<ComplianceDashboardSummary>("/compliance/dashboard");
  return data;
}

export async function fetchAISystems(): Promise<AISystem[]> {
  const { data } = await apiClient.get<AISystem[]>("/ai-systems/");
  return data;
}

export async function fetchResearchNotes(): Promise<ResearchNote[]> {
  const { data } = await apiClient.get<ResearchNote[]>("/research/notes");
  return data;
}

export async function createResearchNote(payload: { title: string; content: string; tags?: string }): Promise<ResearchNote> {
  const { data } = await apiClient.post<ResearchNote>("/research/notes", payload);
  return data;
}

export async function deleteResearchNote(id: string): Promise<void> {
  await apiClient.delete(`/research/notes/${id}`);
}

export async function fetchResearchQueries(): Promise<ResearchQuery[]> {
  const { data } = await apiClient.get<ResearchQuery[]>("/research/queries");
  return data;
}

export async function runResearchQuery(query: string, collection = "regulations"): Promise<ResearchQuery> {
  const { data } = await apiClient.post<ResearchQuery>("/research/queries", { query, collection });
  return data;
}

export async function fetchDocuments(): Promise<DocumentRecord[]> {
  const { data } = await apiClient.get<DocumentRecord[]>("/documents/");
  return data;
}

export async function uploadDocument(file: File, collection: string): Promise<DocumentRecord> {
  const form = new FormData();
  form.append("file", file);
  form.append("collection", collection);
  const { data } = await apiClient.post<DocumentRecord>("/documents/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function deleteDocument(id: string): Promise<void> {
  await apiClient.delete(`/documents/${id}`);
}

type AgentEndpoint = "legal-research" | "compliance" | "risk-evaluation" | "governance-advisor";

export async function askAgent(
  endpoint: AgentEndpoint,
  query: string,
  sessionId?: string
): Promise<AgentQueryResponse> {
  const { data } = await apiClient.post<AgentQueryResponse>(`/agents/${endpoint}`, {
    query,
    session_id: sessionId,
  });
  return data;
}

export async function orchestrateAgents(query: string, sessionId?: string): Promise<OrchestrationResponse> {
  const { data } = await apiClient.post<OrchestrationResponse>("/agents/orchestrate", {
    query,
    session_id: sessionId,
  });
  return data;
}

export async function runCollaboration(query: string, sessionId?: string): Promise<CollaborationResponse> {
  const { data } = await apiClient.post<CollaborationResponse>("/collaboration/", {
    query,
    session_id: sessionId,
  });
  return data;
}

export async function fetchCollaborationRuns(): Promise<CollaborationRunSummary[]> {
  const { data } = await apiClient.get<CollaborationRunSummary[]>("/collaboration/");
  return data;
}

export async function fetchCollaborationRun(runId: string): Promise<CollaborationResponse> {
  const { data } = await apiClient.get<CollaborationResponse>(`/collaboration/${runId}`);
  return data;
}

