export interface ResearchNote {
  id: string;
  title: string;
  content: string;
  tags?: string;
  created_at: string;
  updated_at: string;
}

export interface ResearchQuerySource {
  citation: number;
  document_id: string;
  filename?: string | null;
  clause_number?: string | null;
  chunk_index?: number | null;
  score: number;
  snippet: string;
}

export interface ResearchQuery {
  id: string;
  query: string;
  answer?: string;
  sources: ResearchQuerySource[];
  collection: string;
  created_at: string;
}
