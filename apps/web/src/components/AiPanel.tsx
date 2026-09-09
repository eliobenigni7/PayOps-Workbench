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
          <h2 className="text-base font-semibold">Investigation assistita da AI</h2>
        </div>
        {investigation ? (
          <span className="rounded-full bg-white px-2 py-0.5 text-[11px] font-semibold text-ink-650 ring-1 ring-line">
            Confidenza {Math.round(investigation.confidence * 100)}%
          </span>
        ) : null}
      </div>

      {!available ? (
        <p className="mt-3 text-sm text-ink-650">
          Il provider AI non è disponibile. Evidenze deterministiche, breakdown dello score e risoluzione restano operativi.
        </p>
      ) : null}

      {available && !investigation ? (
        <div className="mt-3">
          <p className="text-sm text-ink-650">
            Opzionale. Il copilot può riassumere i controlli scattati e suggerire cosa verificare. Non può risolvere il caso.
          </p>
          <button
            onClick={onInvestigate}
            disabled={loading}
            className="mt-4 h-10 rounded-lg bg-lime px-4 text-sm font-semibold text-ink-950 disabled:opacity-60"
          >
            {loading ? "Analisi in corso…" : "Chiedi un'investigation"}
          </button>
        </div>
      ) : null}

      {investigation ? (
        <div className="mt-4 space-y-4">
          <p className="text-sm leading-relaxed text-ink-800">{investigation.summary}</p>
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-[0.12em] text-ink-500">Evidenze usate</div>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-ink-800">
              {investigation.evidence.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-[0.12em] text-ink-500">Controlli suggeriti</div>
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-ink-800">
              {investigation.suggested_checks.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <p className="text-xs text-ink-500">
            Fonti usate: storico payroll, eventi HR, batch corrente. {investigation.provider} · {investigation.model}
          </p>
          <p className="text-xs font-medium text-ink-650">
            I suggerimenti AI sono solo informativi. La risoluzione finale richiede conferma dell&apos;operatore.
          </p>
        </div>
      ) : null}
    </section>
  );
}
