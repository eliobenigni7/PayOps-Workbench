"use client";

import Link from "next/link";
import { Sparkle } from "lucide-react";
import { PriorityMark } from "@/components/Badge";
import { formatAge, formatEur, initials } from "@/lib/format";
import type { ExceptionListItem } from "@/lib/types";

export function ExceptionTable({
  rows,
  batchId,
}: {
  rows: ExceptionListItem[];
  batchId?: string;
}) {
  if (rows.length === 0) {
    return (
      <div className="rounded-xl border border-line bg-white px-6 py-16 text-center">
        <h2 className="text-lg font-semibold">No cases need review</h2>
        <p className="mt-2 text-sm text-ink-650">
          Everything in this view passed the current validation rules or was already resolved.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-line bg-white">
      <table className="w-full text-left text-[13px]">
        <thead className="border-b border-line bg-surface-muted text-[11px] font-semibold uppercase tracking-[0.12em] text-ink-500">
          <tr>
            <th className="px-4 py-3">Priority</th>
            <th className="px-4 py-3">Employee</th>
            <th className="px-4 py-3">Issue</th>
            <th className="px-4 py-3">Risk</th>
            <th className="px-4 py-3">Exposure</th>
            <th className="px-4 py-3">Age</th>
            <th className="px-4 py-3">Assignee</th>
            <th className="px-4 py-3" />
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id} className="border-b border-line last:border-0 hover:bg-surface-muted/80">
              <td className={`px-4 py-3 ${row.priority === "critical" ? "border-l-[3px] border-l-[var(--critical)]" : ""}`}>
                <PriorityMark priority={row.priority} />
              </td>
              <td className="px-4 py-3">
                <Link href={`/exceptions/${row.id}${batchId ? `?batch=${batchId}` : ""}`} className="block">
                  <div className="font-semibold text-ink-950">{row.employee_name}</div>
                  <div className="text-xs text-ink-500">
                    {row.employee_id} · {row.team}
                  </div>
                </Link>
              </td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <span>{row.issue_label}</span>
                  {row.has_ai_investigation ? (
                    <Sparkle size={14} className="text-ink-500" aria-label="AI explanation available" />
                  ) : null}
                </div>
              </td>
              <td className="px-4 py-3 font-semibold">{row.risk_score}</td>
              <td className="px-4 py-3">{formatEur(row.financial_exposure)}</td>
              <td className="px-4 py-3 text-ink-650">{formatAge(row.age_hours)}</td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <span className="flex h-7 w-7 items-center justify-center rounded-full bg-surface-muted text-[11px] font-semibold">
                    {initials(row.assigned_to)}
                  </span>
                  <span className="text-ink-650">{row.assigned_to ?? "Unassigned"}</span>
                </div>
              </td>
              <td className="px-4 py-3 text-right">
                <Link
                  href={`/exceptions/${row.id}${batchId ? `?batch=${batchId}` : ""}`}
                  className="text-sm font-semibold text-ink-950"
                >
                  Open
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
