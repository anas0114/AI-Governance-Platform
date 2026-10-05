"use client";

import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";

export default function Topbar() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const clearAuth = useAuthStore((state) => state.clearAuth);

  function handleSignOut() {
    clearAuth();
    router.replace("/login");
  }

  return (
    <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-8">
      <div className="text-sm text-slate-500">Compliance Workspace</div>
      <div className="flex items-center gap-4">
        {user?.email && <span className="text-sm text-slate-600">{user.email}</span>}
        <button
          onClick={handleSignOut}
          className="rounded-md bg-slate-100 px-3 py-1.5 text-sm text-slate-700 hover:bg-slate-200"
        >
          Sign out
        </button>
      </div>
    </header>
  );
}
