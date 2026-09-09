import { Sparkle } from "lucide-react";
import type { Investigation } from "@/lib/types";

export function AiPanel({
  investigation,
  available,
  loading,
  onInvestigate,
}: {
  investigation: Investigation | null;
  available: boolean;
  loading?: boolean;
  onInvestigate: () => void;
}) {
  return (
    <section className="rounded-xl border border-line bg-surface-muted/60 p-5">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Sparkle size={16} />
          <h2 className="text-base font-semibold">AI-assisted investigation</h2>
        </div>
        {investigation ? (
          <span className="rounded-full bg-white px-2 py-0.5 text-[11px] font-semibold text-ink-650 ring-1 ring-line">
            {Math.round(investigation.confidence * 100)}% confidence
          </span>
        ) : null}
      </div>

      {!available ? (
        <p className="mt-3 text-sm text-ink-650">
          The AI provider is unavailable. Deterministic evidence, the score breakdown and resolution still work.
        </p>
      ) : null}

      {available && !investigation ? (
        <div className="mt-3">
          <p className="text-sm text-ink-650">
            Optional. The copilot can summarize the triggered checks and suggest what to verify next. It cannot resolve the case.
          </p>
          <button
            onClick={onInvestigate}
            disabled={loading}
            className="mt-4 h-10 rounded-lg bg-lime px-4 text-sm font-semibold text-ink-950 disabled:opacity-60"
          >
            {loading ? "Investigating…" : "Ask for investigation"}
          </button>
        </div>
      ) : null}

      {investigation ? (
        <div className="mt-4 space-y-4">
          <p className="text-sm leading-relaxed text-ink-800">{investigation.summary}</p>
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-[0.12em] text-ink-500">Evidence used</div>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-ink-800">
              {investigation.evidence.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-[0.12em] text-ink-500">Suggested checks</div>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-ink-800">
              {investigation.suggested_checks.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <p className="text-xs text-ink-500">
            Sources used: payroll history, HR events, current batch. {investigation.provider} · {investigation.model}
          </p>
          <p className="text-xs font-medium text-ink-650">
            AI suggestions are informational only. Final resolution requires operator confirmation.
          </p>
        </div>
      ) : null}
    </section>
  );
}
