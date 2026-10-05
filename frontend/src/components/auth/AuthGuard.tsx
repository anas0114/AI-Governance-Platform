"use client";

import { useEffect, useState } from "react";
import { getValidToken, redirectToLogin } from "@/lib/auth";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    if (getValidToken()) {
      setAuthorized(true);
    } else {
      redirectToLogin();
    }
  }, []);

  if (!authorized) {
    return (
      <div className="flex min-h-screen items-center justify-center text-sm text-slate-500">
        Checking your session…
      </div>
    );
  }

  return <>{children}</>;
}
