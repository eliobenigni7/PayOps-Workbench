"use client";

import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { ExceptionTable } from "@/components/ExceptionTable";
import { api } from "@/lib/api";
import type { DashboardPayload, ExceptionListItem, MetaPayload } from "@/lib/types";

export default function QueuePage() {
  const search = useSearchParams();
  const batchId = search.get("batch") ?? undefined;
  const initialPriority = search.get("priority") ?? "";
  const [meta, setMeta] = useState<MetaPayload | null>(null);
  const [dashboard, setDashboard] = useState<DashboardPayload | null>(null);
  const [items, setItems] = useState<ExceptionListItem[]>([]);
  const [q, setQ] = useState("");
  const [priority, setPriority] = useState(initialPriority);
  const [issueType, setIssueType] = useState("");
  const [assignee, setAssignee] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.meta().then((value) => setMeta(value as MetaPayload)).catch((err: Error) => setError(err.message));
    api.dashboard(batchId).then((value) => setDashboard(value as DashboardPayload)).catch(() => undefined);
  }, [batchId]);

  useEffect(() => {
    api
      .exceptions({
        batch_id: batchId ?? dashboard?.batch.id,
        status: "open",
        priority: priority || undefined,
        issue_type: issueType || undefined,
        assignee: assignee || undefined,
        q: q || undefined,
      })
      .then((payload) => setItems((payload as { items: ExceptionListItem[] }).items))
      .catch((err: Error) => setError(err.message));
  }, [batchId, dashboard?.batch.id, priority, issueType, assignee, q]);

  const operators = useMemo(() => meta?.operators ?? [], [meta]);

  return (
    <AppShell
      title="Coda di review"
      subtitle={`${items.length} aperti`}
      openCount={dashboard?.open_count}
      improvementCount={0}
    >
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <input
          value={q}
          onChange={(event) => setQ(event.target.value)}
          placeholder="Cerca record…"
          className="h-10 w-64 rounded-lg border border-line bg-white px-3 text-sm"
        />
        <select className="h-10 rounded-lg border border-line bg-white px-3 text-sm" value={priority} onChange={(e) => setPriority(e.target.value)}>
          <option value="">Tutte le priorità</option>
          <option value="critical">Critico</option>
          <option value="high">Alto</option>
          <option value="medium">Medio</option>
          <option value="low">Basso</option>
        </select>
        <select className="h-10 rounded-lg border border-line bg-white px-3 text-sm" value={issueType} onChange={(e) => setIssueType(e.target.value)}>
          <option value="">Tutti i tipi di problema</option>
          {(meta?.issue_types ?? []).map((item) => (
            <option key={item.value} value={item.value}>
              {item.label}
            </option>
          ))}
        </select>
        <select className="h-10 rounded-lg border border-line bg-white px-3 text-sm" value={assignee} onChange={(e) => setAssignee(e.target.value)}>
          <option value="">Tutti gli assegnatari</option>
          <option value="unassigned">Non assegnato</option>
          {operators.map((name) => (
            <option key={name}>{name}</option>
          ))}
        </select>
      </div>
      {error ? <p className="mb-3 text-sm text-[var(--critical)]">{error}</p> : null}
      <ExceptionTable rows={items} batchId={dashboard?.batch.id} />
    </AppShell>
  );
}
