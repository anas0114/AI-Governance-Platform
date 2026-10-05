export interface DocumentRecord {
  id: string;
  filename: string;
  collection: string;
  content_type?: string | null;
  chunk_count: number;
  created_at: string;
}
