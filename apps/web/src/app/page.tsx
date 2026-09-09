"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { BarList } from "@/components/BarList";
import { ExceptionTable } from "@/components/ExceptionTable";
import { KpiCard } from "@/components/KpiCard";
import { api } from "@/lib/api";
import { formatAge, formatNumber, formatShare, monthLabel } from "@/lib/format";
import type { DashboardPayload, Opportunity } from "@/lib/types";

export default function OverviewPage() {
  const search = useSearchParams();
  const batchId = search.get("batch") ?? undefined;
  const [data, setData] = useState<DashboardPayload | null>(null);
  const [opps, setOpps] = useState<Opportunity[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [importing, setImporting] = useState(false);

  useEffect(() => {
    Promise.all([api.dashboard(batchId) as Promise<DashboardPayload>, api.improvements() as Promise<{ items: Opportunity[] }>])
      .then(([dashboard, improvements]) => {
        setData(dashboard);
        setOpps(improvements.items);
      })
      .catch((err: Error) => setError(err.message));
  }, [batchId]);

  if (error) {
    return (
      <AppShell title="Centro di controllo operativo">
        <p className="text-sm text-[var(--critical)]">{error}</p>
      </AppShell>
    );
  }
  if (!data) {
    return (
      <AppShell title="Centro di controllo operativo">
        <div className="grid grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <div key={index} className="skeleton h-28 rounded-xl" />
          ))}
        </div>
      </AppShell>
    );
  }

  const importAction = (
    <label className="inline-flex h-10 cursor-pointer items-center rounded-lg bg-lime px-4 text-sm font-semibold text-ink-950">
      {importing ? "Import in corso…" : "Importa batch"}
      <input
        type="file"
        accept=".csv"
        className="hidden"
        onChange={async (event) => {
          const file = event.target.files?.[0];
          if (!file) return;
          setImporting(true);
          try {
            await api.importBatch(file);
            window.location.reload();
          } catch (err) {
            setError(err instanceof Error ? err.message : "Import fallito");
          } finally {
            setImporting(false);
          }
        }}
      />
    </label>
  );

  return (
    <AppShell
      title="Centro di controllo operativo"
      subtitle={`Batch payroll · ${monthLabel(data.batch.period)}`}
      actions={importAction}
      openCount={data.open_count}
      improvementCount={opps.length}
    >
      <p className="mb-5 text-sm text-ink-650">
        Batch processato · {formatNumber(data.processed)} record
        {data.batch.processed_at ? ` · ultimo aggiornamento ${data.batch.processed_at.slice(11, 16)}` : ""}
      </p>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        <KpiCard label="Processati" value={formatNumber(data.processed)} />
        <KpiCard
          label="Auto-chiusi"
          value={formatNumber(data.auto_cleared)}
          hint={formatShare(data.auto_cleared_rate)}
          accent
        />
        <KpiCard
          label="Da rivedere"
          value={formatNumber(data.needs_review)}
          hint={formatShare(data.review_rate)}
        />
        <KpiCard
          label="Critici"
          value={formatNumber(data.critical)}
          hint={`${data.critical_delta >= 0 ? "+" : ""}${data.critical_delta} vs batch precedente`}
          critical
        />
      </div>

      <div className="mt-4 rounded-xl bg-lime-soft p-5">
        <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink-650">
          Effort manuale stimato evitato oggi
        </div>
        <div className="mt-2 flex flex-wrap items-end justify-between gap-4">
          <div className="text-[32px] font-bold leading-none">{data.effort_avoided_label}</div>
          <p className="max-w-xl text-sm text-ink-650">
            Ipotesi: {String(data.baseline_seconds_per_record).replace(".", ",")}s di sguardo su ogni record auto-cleared.
            Assunzione di scenario di questo demo sintetico — non un esito payroll misurato.
          </p>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 xl:grid-cols-3">
        <section className="xl:col-span-2">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-lg font-bold">Anteprima coda di review</h2>
            <Link href={`/exceptions${batchId ? `?batch=${batchId}` : ""}`} className="text-sm font-semibold">
              Apri la coda →
            </Link>
          </div>
          <ExceptionTable rows={data.queue_preview} batchId={data.batch.id} />
        </section>
        <div className="space-y-4">
          <section className="rounded-xl border border-line bg-white p-5">
            <h2 className="text-base font-semibold">Principali cause di eccezione</h2>
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
            <h2 className="text-base font-semibold">I più vecchi ancora aperti</h2>
            <ul className="mt-3 space-y-3">
              {data.oldest_unresolved.map((item) => (
                <li key={item.id} className="flex items-center justify-between gap-3 text-sm">
                  <Link href={`/exceptions/${item.id}`} className="font-medium">
                    {item.employee_id} · {item.issue_label}
                  </Link>
                  <span className="text-ink-500">{formatAge(item.age_hours)}</span>
                </li>
              ))}
            </ul>
          </section>
        </div>
      </div>
    </AppShell>
  );
}
