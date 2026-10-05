export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatSource {
  citation: number;
  document_id: string;
  filename?: string | null;
  clause_number?: string | null;
  chunk_index?: number | null;
  score: number;
  snippet: string;
}

export interface ChatResponse {
  answer: string;
  sources: ChatSource[];
}
