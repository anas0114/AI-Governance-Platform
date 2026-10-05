"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { isAxiosError } from "axios";
import { fetchCurrentUser, login, registerUser } from "@/lib/api";
import { getValidToken } from "@/lib/auth";
import { useAuthStore } from "@/store/authStore";

function getNextPath(): string {
  const next = new URLSearchParams(window.location.search).get("next");
  // Only allow same-site relative paths to avoid open redirects.
  return next && next.startsWith("/") && !next.startsWith("//") ? next : "/dashboard";
}

export default function LoginPage() {
  const router = useRouter();
  const setAuth = useAuthStore((state) => state.setAuth);
  const [mode, setMode] = useState<"signin" | "register">("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (getValidToken()) router.replace(getNextPath());
  }, [router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      if (mode === "register") {
        await registerUser({ email, password, full_name: fullName || undefined });
      }
      const token = await login(email, password);
      localStorage.setItem("access_token", token);
      const user = await fetchCurrentUser();
      setAuth(user, token);
      router.replace(getNextPath());
    } catch (err) {
      if (isAxiosError(err) && !err.response) {
        setError("Cannot reach the API server. Make sure the backend is running on port 8000.");
      } else if (isAxiosError(err) && mode === "register" && err.response?.status === 400) {
        setError("That email is already registered. Sign in instead.");
      } else {
        setError(mode === "register" ? "Registration failed." : "Invalid email or password.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="w-full max-w-sm rounded-lg bg-white p-8 shadow">
      <h1 className="text-xl font-semibold text-slate-900">
        {mode === "signin" ? "Sign in" : "Create account"}
      </h1>
      <form className="mt-6 flex flex-col gap-4" onSubmit={handleSubmit}>
        {mode === "register" && (
          <input
            type="text"
            placeholder="Full name (optional)"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
        )}
        <input
          type="email"
          placeholder="Email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="rounded-md border border-slate-300 px-3 py-2 text-sm"
        />
        <input
          type="password"
          placeholder="Password"
          required
          minLength={mode === "register" ? 8 : undefined}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="rounded-md border border-slate-300 px-3 py-2 text-sm"
        />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-brand-600 px-3 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60"
        >
          {loading ? "Please wait..." : mode === "signin" ? "Sign in" : "Create account"}
        </button>
      </form>
      <button
        type="button"
        onClick={() => {
          setMode(mode === "signin" ? "register" : "signin");
          setError(null);
        }}
        className="mt-4 w-full text-center text-sm text-brand-600 hover:underline"
      >
        {mode === "signin" ? "Don't have an account? Create one" : "Already have an account? Sign in"}
      </button>
    </div>
  );
}
