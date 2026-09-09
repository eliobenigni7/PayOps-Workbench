export function BarList({
  items,
}: {
  items: { label: string; value: number; hint?: string }[];
}) {
  const max = Math.max(...items.map((item) => item.value), 1);
  return (
    <div className="space-y-3">
      {items.map((item, index) => (
        <div key={item.label}>
          <div className="mb-1 flex items-baseline justify-between gap-3 text-sm">
            <span className="font-medium text-ink-800">{item.label}</span>
            <span className="text-ink-650">{item.hint ?? item.value}</span>
          </div>
          <div className="h-2 rounded-full bg-surface-muted">
            <div
              className={`h-2 rounded-full ${index === 0 ? "bg-lime" : "bg-ink-950"}`}
              style={{ width: `${Math.max(6, (item.value / max) * 100)}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
