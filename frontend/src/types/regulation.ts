export interface Regulation {
  id: string;
  title: string;
  jurisdiction?: string;
  category?: string;
  summary?: string;
  source_url?: string;
  effective_date?: string;
  status: "tracked" | "in_force" | "proposed" | "repealed";
  created_at: string;
  updated_at: string;
}

export interface RegulationClause {
  id: string;
  regulation_id: string;
  clause_number: string;
  title?: string;
  text: string;
  created_at: string;
}
