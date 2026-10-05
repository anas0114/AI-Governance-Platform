import Link from "next/link";

const navItems = [
  { href: "/dashboard", label: "Overview" },
  { href: "/regulations", label: "Regulation Repository" },
  { href: "/policies", label: "Policies" },
  { href: "/ai-systems", label: "AI Systems" },
  { href: "/compliance", label: "Compliance" },
  { href: "/audits", label: "Audits" },
  { href: "/documents", label: "Documents" },
  { href: "/research", label: "Research Workspace" },
  { href: "/agents", label: "Governance Agents" },
  { href: "/collaboration", label: "Agent Collaboration" },
  { href: "/chat", label: "AI Copilot" },
];

export default function Sidebar() {
  return (
    <aside className="w-64 shrink-0 border-r border-slate-200/80 bg-[#10272a] p-6 text-white">
      <div className="mb-2 text-xs font-semibold uppercase tracking-[0.22em] text-teal-200">AIGOV / 01</div>
      <div className="mb-8 text-xl font-semibold tracking-tight">AI Governance</div>
      <nav className="flex flex-col gap-1">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="rounded-md px-3 py-2 text-sm text-slate-300 transition-colors hover:bg-white/10 hover:text-white"
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
