import Link from "next/link";

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 p-24 text-center">
      <h1 className="text-4xl font-bold text-slate-900">
        AI Governance &amp; Compliance Platform
      </h1>
      <p className="max-w-xl text-slate-600">
        Manage policies, assess compliance against regulatory frameworks, run
        audits, and chat with an AI copilot grounded in your governance
        documents.
      </p>
      <Link
        href="/login"
        className="rounded-md bg-brand-600 px-6 py-3 text-white hover:bg-brand-700"
      >
        Sign in to continue
      </Link>
    </main>
  );
}
