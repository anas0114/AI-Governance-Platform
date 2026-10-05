export interface AuthUser {
  id: string;
  email: string;
  full_name?: string;
  role: "admin" | "compliance_officer" | "auditor" | "viewer";
}

export interface LoginPayload {
  username: string;
  password: string;
}
