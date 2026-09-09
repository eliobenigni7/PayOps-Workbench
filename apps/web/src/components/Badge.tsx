import type { Priority } from "@/lib/types";

const styles: Record<string, string> = {
  critical: "text-[var(--critical)] bg-[var(--critical-soft)]",
  high: "text-[var(--high)] bg-[var(--high-soft)]",
  medium: "text-[var(--medium)] bg-[var(--medium-soft)]",
  low: "text-ink-650 bg-surface-muted",
  success: "text-[var(--success)] bg-[var(--success-soft)]",
  info: "text-[var(--info)] bg-[var(--info-soft)]",
  neutral: "text-ink-650 bg-surface-muted",
};

export function Badge({
  children,
  tone = "neutral",
  dot = false,
}: {
  children: React.ReactNode;
  tone?: string;
  dot?: boolean;
}) {
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-[11px] font-semibold ${styles[tone] ?? styles.neutral}`}>
      {dot ? <span className="h-1.5 w-1.5 rounded-full bg-current" /> : null}
      {children}
    </span>
  );
}

export function PriorityMark({ priority }: { priority: Priority }) {
  return <Badge tone={priority} dot>{priority[0].toUpperCase() + priority.slice(1)}</Badge>;
}
