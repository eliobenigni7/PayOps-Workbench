"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { AiPanel } from "@/components/AiPanel";
import { Badge, PriorityMark } from "@/components/Badge";
import { ResolutionDrawer } from "@/components/ResolutionDrawer";
import { api } from "@/lib/api";
import { formatEur, formatPct, monthLabel, titleCase } from "@/lib/format";
import type { ExceptionDetail, MetaPayload } from "@/lib/types";

function formatValue(value: string | number, format?: string) {
  if (format === "eur" && typeof value === "number") return formatEur(value);
  if (format === "pct" && typeof value === "number") return formatPct(value, true);
  return String(value);
}

export default function ExceptionDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [data, setData] = useState<ExceptionDetail | null>(null);
  const [meta, setMeta] = useState<MetaPayload | null>(null);
  const [outcome, setOutcome] = useState<string | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.exception(params.id).then((value) => setData(value as ExceptionDetail)).catch((err: Error) => setError(err.message));
    api.meta().then((value) => setMeta(value as MetaPayload)).catch(() => undefined);
  }, [params.id]);

  if (error) {
    return (
      <AppShell title="Exception">
        <p className="text-sm text-[var(--critical)]">{error}</p>
      </AppShell>
    );
  }
  if (!data) {
    return (
      <AppShell title="Exception">
        <div className="skeleton h-64 rounded-xl" />
      </AppShell>
    );
  }

  const scoreTotal = data.priority_breakdown.reduce((sum, item) => sum + item.value, 0);

  return (
    <AppShell
      title={data.issue_label}
      subtitle={`${data.employee_id} · ${data.team} · ${monthLabel(data.period)}`}
      back={{ href: "/exceptions", label: "Review queue" }}
    >
      <div className="mb-5 flex flex-wrap items-center gap-3">
        <PriorityMark priority={data.priority} />
        <span className="text-sm text-ink-650">Risk {data.risk_score}</span>
        <Badge tone={data.status === "resolved" ? "success" : "neutral"}>{titleCase(data.status)}</Badge>
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <section className="rounded-xl border border-line bg-white p-5">
          <h2 className="text-base font-semibold">{data.context_panel.title}</h2>
          <dl className="mt-4 space-y-3">
            {data.context_panel.rows.map((row) => (
              <div key={row.label} className="flex items-baseline justify-between gap-4 text-sm">
                <dt className="text-ink-650">{row.label}</dt>
                <dd className={`font-semibold ${row.tone === "critical" ? "text-[var(--critical)]" : ""}`}>
                  {formatValue(row.value, row.format)}
                </dd>
              </div>
            ))}
          </dl>
        </section>
        <section className="rounded-xl border border-line bg-white p-5">
          <h2 className="text-base font-semibold">Why is this {data.priority}?</h2>
          <p className="mt-1 text-sm text-ink-650">Interpretable priority breakdown. This is not an AI score.</p>
          <dl className="mt-4 space-y-3">
            {data.priority_breakdown.map((item) => (
              <div key={item.component}>
                <div className="flex items-baseline justify-between text-sm">
                  <dt className="font-medium">{titleCase(item.component)}</dt>
                  <dd className="font-semibold">+{item.value}</dd>
                </div>
                <p className="text-xs text-ink-500">{item.explanation}</p>
              </div>
            ))}
            <div className="flex items-baseline justify-between border-t border-line pt-3 text-sm font-bold">
              <dt>Total</dt>
              <dd>{scoreTotal}</dd>
            </div>
          </dl>
        </section>
      </div>

      <section className="mt-4 rounded-xl border border-line bg-white p-5">
        <h2 className="text-base font-semibold">Triggered checks</h2>
        <ul className="mt-3 space-y-2">
          {data.triggered_rules.map((rule) => (
            <li key={rule.rule_id} className="flex items-start gap-3 rounded-lg bg-surface-muted px-3 py-3 text-sm">
              <Badge tone={rule.severity} dot>
                {titleCase(rule.severity)}
              </Badge>
              <div>
                <div className="font-semibold">{rule.rule_id.replaceAll("_", " ")}</div>
                <div className="text-ink-650">{rule.message}</div>
              </div>
            </li>
          ))}
        </ul>
      </section>

      <section className="mt-4 rounded-xl border border-line bg-white p-5">
        <h2 className="text-base font-semibold">Related HR events</h2>
        <ul className="mt-3 space-y-2 text-sm">
          {data.hr_events.map((event) => (
            <li key={event.type} className="flex items-start justify-between gap-4">
              <span>{event.note}</span>
              <Badge tone={event.present ? "success" : "critical"}>{event.present ? "Present" : "Missing"}</Badge>
            </li>
          ))}
        </ul>
      </section>

      <div className="mt-4">
        <AiPanel
          investigation={data.investigation}
          available={data.ai_available}
          loading={aiLoading}
          onInvestigate={async () => {
            setAiLoading(true);
            try {
              const payload = (await api.investigate(data.id)) as { investigation?: ExceptionDetail["investigation"] };
              if (payload.investigation) {
                setData({ ...data, investigation: payload.investigation, has_ai_investigation: true });
              }
            } finally {
              setAiLoading(false);
            }
          }}
        />
      </div>

      <section className="mt-4 rounded-xl border border-line bg-white p-5">
        <h2 className="text-base font-semibold">Resolution</h2>
        {data.resolution ? (
          <p className="mt-3 text-sm text-ink-800">
            {data.resolution.outcome_label} · {data.resolution.reason_label} · {data.resolution.resolved_by}
            {data.resolution.note ? ` — ${data.resolution.note}` : ""}
          </p>
        ) : (
          <div className="mt-4 flex flex-wrap gap-2">
            <button className="h-10 rounded-lg bg-ink-950 px-4 text-sm font-semibold text-white" onClick={() => setOutcome("confirm_issue")}>
              Confirm issue
            </button>
            <button className="h-10 rounded-lg border border-line px-4 text-sm font-semibold" onClick={() => setOutcome("mark_expected")}>
              Mark as expected
            </button>
            <button className="h-10 rounded-lg border border-line px-4 text-sm font-semibold" onClick={() => setOutcome("request_info")}>
              Request information
            </button>
            <button className="h-10 rounded-lg border border-[var(--critical)] px-4 text-sm font-semibold text-[var(--critical)]" onClick={() => setOutcome("escalate")}>
              Escalate
            </button>
          </div>
        )}
      </section>

      <section className="mt-4 rounded-xl border border-line bg-white p-5">
        <h2 className="text-base font-semibold">Audit history</h2>
        <ol className="mt-3 space-y-2 text-sm">
          {data.audit.map((event) => (
            <li key={event.id} className="flex justify-between gap-4">
              <span>
                {titleCase(event.event_type)} · {event.actor}
              </span>
              <span className="text-ink-500">{event.created_at.replace("T", " ").slice(0, 16)}</span>
            </li>
          ))}
        </ol>
      </section>

      <ResolutionDrawer
        open={Boolean(outcome)}
        outcome={outcome}
        meta={meta}
        onClose={() => setOutcome(null)}
        onSubmit={async (payload) => {
          const updated = (await api.resolve(data.id, payload)) as ExceptionDetail;
          setData(updated);
          setOutcome(null);
          router.refresh();
        }}
      />
    </AppShell>
  );
}
