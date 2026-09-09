"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/AppShell";
import { Badge } from "@/components/Badge";
import { api } from "@/lib/api";
import type { Opportunity } from "@/lib/types";

export default function ImprovementsPage() {
  const [items, setItems] = useState<Opportunity[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .improvements()
      .then((payload) => setItems((payload as { items: Opportunity[] }).items))
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <AppShell title="Opportunità di miglioramento" subtitle="Sistemare la fonte del lavoro di review ricorrente" improvementCount={items.length}>
      {error ? <p className="text-sm text-[var(--critical)]">{error}</p> : null}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {items.map((item) => (
          <Link key={item.id} href={`/improvements/${item.id}`} className="rounded-xl border border-line bg-white p-5 hover:bg-surface-muted/60">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-lg font-bold">{item.title}</h2>
              <Badge tone="success">{item.impact_label}</Badge>
            </div>
            <p className="mt-2 text-sm text-ink-650">{item.effort_label}</p>
            <dl className="mt-4 grid grid-cols-3 gap-3 text-sm">
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.12em] text-ink-500">Casi / mese</dt>
                <dd className="mt-1 text-lg font-bold">{item.monthly_occurrences}</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.12em] text-ink-500">Gestione</dt>
                <dd className="mt-1 text-lg font-bold">{item.avg_handling_minutes}m</dd>
              </div>
              <div>
                <dt className="text-[11px] font-semibold uppercase tracking-[0.12em] text-ink-500">Effort</dt>
                <dd className="mt-1 text-lg font-bold">{item.monthly_effort_hours}h</dd>
              </div>
            </dl>
          </Link>
        ))}
      </div>
    </AppShell>
  );
}
