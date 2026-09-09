"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { BarList } from "@/components/BarList";
import { Badge } from "@/components/Badge";
import { api } from "@/lib/api";
import { formatNumber, formatPct, formatShare, monthLabel } from "@/lib/format";
import { RULE_LABELS, TREND_LABELS, labelOf } from "@/lib/labels";
import type { InsightsPayload } from "@/lib/types";

export default function InsightsPage() {
  const [data, setData] = useState<InsightsPayload | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.insights().then((value) => setData(value as InsightsPayload)).catch((err: Error) => setError(err.message));
  }, []);

  if (error) {
    return (
      <AppShell title="Analisi operative">
        <p className="text-sm text-[var(--critical)]">{error}</p>
      </AppShell>
    );
  }
  if (!data) {
    return (
      <AppShell title="Analisi operative">
        <div className="skeleton h-64 rounded-xl" />
      </AppShell>
    );
  }

  return (
    <AppShell
      title="Analisi operative"
      subtitle={`${monthLabel(data.period)}${data.previous_period ? ` vs ${monthLabel(data.previous_period)}` : ""}`}
      improvementCount={data.opportunities.length}
    >
      <p className="mb-6 max-w-2xl text-lg font-semibold leading-snug">{data.hero_question}</p>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <section className="rounded-xl border border-line bg-white p-5">
          <h2 className="text-base font-semibold">Principali fonti di review manuale</h2>
          <div className="mt-4">
            <BarList
              items={data.top_causes.map((item) => ({
                label: item.label,
                value: item.occurrences,
                hint: formatShare(item.share),
              }))}
            />
          </div>
        </section>
        <section className="rounded-xl border border-line bg-white p-5">
          <h2 className="text-base font-semibold">Opportunità di miglioramento</h2>
          <div className="mt-4 space-y-3">
            {data.opportunities.map((item) => (
              <Link key={item.id} href={`/improvements/${item.id}`} className="block rounded-xl border border-line p-4 hover:bg-surface-muted">
                <div className="flex items-center justify-between gap-3">
                  <div className="font-semibold">{item.title}</div>
                  <Badge tone="success">{item.impact_label}</Badge>
                </div>
                <p className="mt-2 text-sm text-ink-650">
                  {item.monthly_occurrences} casi · {item.monthly_effort_hours}h / mese · {item.effort_label}
                </p>
              </Link>
            ))}
          </div>
        </section>
      </div>

      <section className="mt-4 overflow-hidden rounded-xl border border-line bg-white">
        <div className="border-b border-line px-5 py-4">
          <h2 className="text-base font-semibold">Effort per tipo di problema</h2>
        </div>
        <table className="w-full text-left text-sm">
          <thead className="bg-surface-muted text-[11px] font-semibold uppercase tracking-[0.12em] text-ink-500">
            <tr>
              <th className="px-5 py-3">Problema</th>
              <th className="px-5 py-3">Occorrenze</th>
              <th className="px-5 py-3">Gestione media</th>
              <th className="px-5 py-3">Ore</th>
              <th className="px-5 py-3">Falsi positivi</th>
              <th className="px-5 py-3">Trend</th>
            </tr>
          </thead>
          <tbody>
            {data.effort_by_issue.map((row) => (
              <tr key={row.issue_type} className="border-t border-line">
                <td className="px-5 py-3 font-medium">{row.label}</td>
                <td className="px-5 py-3">{formatNumber(row.occurrences)}</td>
                <td className="px-5 py-3">{row.avg_handling_minutes} min</td>
                <td className="px-5 py-3">{row.monthly_effort_hours}h</td>
                <td className="px-5 py-3">{formatPct((row.false_positive_rate ?? 0) * 100)}</td>
                <td className="px-5 py-3">{labelOf(TREND_LABELS, row.trend ?? "stable")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="mt-4 overflow-hidden rounded-xl border border-line bg-white">
        <div className="border-b border-line px-5 py-4">
          <h2 className="text-base font-semibold">Qualità delle regole</h2>
          <p className="mt-1 text-sm text-ink-650">Anche l&apos;automazione va migliorata in continuo.</p>
        </div>
        <table className="w-full text-left text-sm">
          <thead className="bg-surface-muted text-[11px] font-semibold uppercase tracking-[0.12em] text-ink-500">
            <tr>
              <th className="px-5 py-3">Regola</th>
              <th className="px-5 py-3">Trigger</th>
              <th className="px-5 py-3">Confermate</th>
              <th className="px-5 py-3">Falsi positivi</th>
              <th className="px-5 py-3">Gestione</th>
            </tr>
          </thead>
          <tbody>
            {data.rule_quality.map((row) => (
              <tr key={row.rule_id} className="border-t border-line">
                <td className="px-5 py-3 font-medium">{labelOf(RULE_LABELS, row.rule_id)}</td>
                <td className="px-5 py-3">{row.trigger_count}</td>
                <td className="px-5 py-3">{row.confirmed_issue_rate == null ? "—" : formatPct(row.confirmed_issue_rate * 100)}</td>
                <td className="px-5 py-3">{row.false_positive_rate == null ? "—" : formatPct(row.false_positive_rate * 100)}</td>
                <td className="px-5 py-3">{row.avg_handling_minutes == null ? "—" : `${row.avg_handling_minutes} min`}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <p className="mt-4 max-w-3xl text-xs text-ink-500">{data.methodology.note}</p>
    </AppShell>
  );
}
