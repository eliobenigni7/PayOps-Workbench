"use client";

import { useState } from "react";
import type { MetaPayload } from "@/lib/types";

const OUTCOME_HELP: Record<string, string> = {
  confirm_issue: "The exception is a real operational issue.",
  mark_expected: "The values are unusual but legitimate.",
  request_info: "The case stays open until missing evidence arrives.",
  escalate: "Hand the case to a lead without changing source data.",
};

export function ResolutionDrawer({
  open,
  outcome,
  meta,
  onClose,
  onSubmit,
}: {
  open: boolean;
  outcome: string | null;
  meta: MetaPayload | null;
  onClose: () => void;
  onSubmit: (payload: { outcome: string; reason_code: string; note: string; resolved_by: string }) => Promise<void>;
}) {
  const [reason, setReason] = useState("salary_increase");
  const [note, setNote] = useState("");
  const [resolvedBy, setResolvedBy] = useState(meta?.operators[0] ?? "Sofia Bianchi");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!open || !outcome) return null;
  const label = meta?.outcomes.find((item) => item.value === outcome)?.label ?? outcome;

  return (
    <div className="fixed inset-0 z-40 flex justify-end bg-ink-950/20">
      <button className="flex-1 cursor-default" onClick={onClose} aria-label="Close resolution drawer" />
      <aside className="h-full w-[420px] bg-white p-6 shadow-drawer">
        <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-ink-500">Resolve case</div>
        <h2 className="mt-2 text-xl font-bold">{label}</h2>
        <p className="mt-2 text-sm text-ink-650">{OUTCOME_HELP[outcome]}</p>
        <p className="mt-2 text-sm text-ink-650">A structured reason is required so Insights can learn from the outcome.</p>

        <form
          className="mt-6 space-y-5"
          onSubmit={async (event) => {
            event.preventDefault();
            setBusy(true);
            setError(null);
            try {
              await onSubmit({ outcome, reason_code: reason, note, resolved_by: resolvedBy });
            } catch (err) {
              setError(err instanceof Error ? err.message : "Could not resolve the case");
              setBusy(false);
            }
          }}
        >
          <label className="block">
            <span className="mb-1 block text-xs font-semibold uppercase tracking-[0.12em] text-ink-500">Reason</span>
            <div className="space-y-2">
              {(meta?.reason_codes ?? []).map((item) => (
                <label key={item.value} className="flex items-center gap-2 text-sm">
                  <input
                    type="radio"
                    name="reason"
                    value={item.value}
                    checked={reason === item.value}
                    onChange={() => setReason(item.value)}
                  />
                  {item.label}
                </label>
              ))}
            </div>
          </label>
          <label className="block">
            <span className="mb-1 block text-xs font-semibold uppercase tracking-[0.12em] text-ink-500">Operator</span>
            <select
              className="h-10 w-full rounded-lg border border-line bg-white px-3 text-sm"
              value={resolvedBy}
              onChange={(event) => setResolvedBy(event.target.value)}
            >
              {(meta?.operators ?? ["Sofia Bianchi"]).map((name) => (
                <option key={name}>{name}</option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="mb-1 block text-xs font-semibold uppercase tracking-[0.12em] text-ink-500">Note (optional)</span>
            <textarea
              className="h-24 w-full rounded-lg border border-line px-3 py-2 text-sm"
              value={note}
              onChange={(event) => setNote(event.target.value)}
            />
          </label>
          {error ? <p className="text-sm text-[var(--critical)]">{error}</p> : null}
          <div className="flex justify-end gap-2">
            <button type="button" className="h-10 rounded-lg px-4 text-sm font-semibold" onClick={onClose}>
              Cancel
            </button>
            <button
              type="submit"
              disabled={busy}
              className="h-10 rounded-lg bg-ink-950 px-4 text-sm font-semibold text-white disabled:opacity-60"
            >
              {busy ? "Saving…" : "Resolve case"}
            </button>
          </div>
        </form>
      </aside>
    </div>
  );
}
