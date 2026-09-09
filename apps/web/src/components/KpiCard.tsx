export function KpiCard({
  label,
  value,
  hint,
  accent = false,
  critical = false,
}: {
  label: string;
  value: string;
  hint?: string;
  accent?: boolean;
  critical?: boolean;
}) {
  return (
    <div className="rounded-xl border border-line bg-white p-5">
      <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink-500">{label}</div>
      <div className="mt-2 flex items-center gap-2">
        {critical ? <span className="h-2 w-2 rounded-full bg-[var(--critical)]" /> : null}
        <div className="text-[30px] font-bold leading-none tracking-tight">{value}</div>
      </div>
      {hint ? <div className="mt-2 text-sm text-ink-650">{hint}</div> : null}
      {accent ? <div className="mt-3 h-1 w-10 rounded-full bg-lime" /> : null}
    </div>
  );
}
