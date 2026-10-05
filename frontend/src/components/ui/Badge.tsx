import { clsx } from "clsx";

const styles: Record<string, string> = {
  low: "bg-emerald-100 text-emerald-800",
  minimal: "bg-emerald-100 text-emerald-800",
  medium: "bg-amber-100 text-amber-800",
  limited: "bg-amber-100 text-amber-800",
  high: "bg-orange-100 text-orange-800",
  critical: "bg-red-100 text-red-800",
  unacceptable: "bg-red-100 text-red-800",
  unclassified: "bg-slate-100 text-slate-700",
};

export default function Badge({ level, children }: { level: string; children: React.ReactNode }) {
  return (
    <span className={clsx("rounded-full px-2.5 py-0.5 text-xs font-medium", styles[level] ?? styles.unclassified)}>
      {children}
    </span>
  );
}
