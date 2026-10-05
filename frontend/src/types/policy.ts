export interface Policy {
  id: string;
  title: string;
  description?: string;
  content?: string;
  version: number;
  status: "draft" | "in_review" | "approved" | "retired";
  created_at: string;
  updated_at: string;
}
