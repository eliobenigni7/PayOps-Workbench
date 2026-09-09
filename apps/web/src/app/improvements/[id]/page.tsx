"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { Badge } from "@/components/Badge";
import { api } from "@/lib/api";
import { titleCase } from "@/lib/format";
import type { Opportunity } from "@/lib/types";

const STATUSES = ["detected", "investigate", "planned", "implemented", "dismissed"];

export default function ImprovementDetailPage() {
  const params = useParams<{ id: string }>();
  const [item, setItem] = useState<Opportunity | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.improvement(params.id).then((value) => setItem(value as Opportunity)).catch((err: Error) => setError(err.message));
  }, [params.id]);

  if (error) {
    return (
      <AppShell title="Improvement opportunity">
        <p className="text-sm text-[var(--critical)]">{error}</p>
      </AppShell>
    );
  }
  if (!item) {
    return (
      <AppShell title="Improvement opportunity">
        <div className="skeleton h-64 rounded-xl" />
      </AppShell>
    );
  }

  return (
    <AppShell title={item.title} subtitle={`${item.impact_label} · ${item.effort_label}`} back={{ href: "/improvements", label: "Improvements" }}>
      <div className="flex items-center gap-2">
        <Badge tone="success">{item.impact_label}</Badge>
        <Badge>{item.effort_label}</Badge>
        <Badge tone="info">{titleCase(item.status)}</Badge>
      </div>

      <section className="mt-5 grid grid-cols-3 gap-4">
        <div className="rounded-xl border border-line bg-white p-5">
          <div className="text-[11px] font-semibold uppercase tracking-[0.12em] text-ink-500">Cases / month</div>
          <div className="mt-2 text-3xl font-bold">{item.monthly_occurrences}</div>
        </div>
        <div className="rounded-xl border border-line bg-white p-5">
          <div className="text-[11px] font-semibold uppercase tracking-[0.12em] text-ink-500">Avg handling time</div>
          <div className="mt-2 text-3xl font-bold">{item.avg_handling_minutes} min</div>
        </div>
        <div className="rounded-xl border border-line bg-lime-soft p-5">
          <div className="text-[11px] font-semibold uppercase tracking-[0.12em] text-ink-650">Manual effort / month</div>
          <div className="mt-2 text-3xl font-bold">{item.monthly_effort_hours}h</div>
          <div className="mt-1 text-sm text-ink-650">{item.expected_effort_removed_hours}h removable if the source is fixed</div>
        </div>
      </section>

      <div className="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-2">
        <section className="rounded-xl border border-line bg-white p-5">
          <h2 className="text-base font-semibold">Root-cause hypothesis</h2>
          <p className="mt-3 text-sm leading-relaxed text-ink-800">{item.root_cause_hypothesis}</p>
        </section>
        <section className="rounded-xl border border-line bg-white p-5">
          <h2 className="text-base font-semibold">Suggested intervention</h2>
          <p className="mt-3 text-sm leading-relaxed text-ink-800">{item.suggested_intervention}</p>
        </section>
      </div>

      <section className="mt-4 rounded-xl border border-line bg-white p-5">
        <h2 className="text-base font-semibold">Expected effect</h2>
        <p className="mt-3 text-sm leading-relaxed text-ink-800">{item.expected_impact}</p>
        <h3 className="mt-5 text-sm font-semibold">Measure after release</h3>
        <ul className="mt-2 list-disc pl-5 text-sm text-ink-800">
          {item.measurement_kpis.map((kpi) => (
            <li key={kpi}>{kpi}</li>
          ))}
        </ul>
      </section>

      <section className="mt-4 rounded-xl border border-line bg-white p-5">
        <h2 className="text-base font-semibold">Opportunity status</h2>
        <div className="mt-4 flex flex-wrap gap-2">
          {STATUSES.map((status) => (
            <button
              key={status}
              onClick={async () => {
                const updated = (await api.updateImprovement(item.id, status)) as Opportunity;
                setItem(updated);
              }}
              className={`h-10 rounded-lg px-4 text-sm font-semibold ${
                item.status === status ? "bg-lime text-ink-950" : "border border-line bg-white"
              }`}
            >
              {titleCase(status)}
            </button>
          ))}
        </div>
      </section>
    </AppShell>
  );
}
