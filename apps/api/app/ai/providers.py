from __future__ import annotations

from typing import Protocol

from app.domain.types import NormalizedRecord, RuleEvaluation


class InvestigationDraft(dict):
    pass


class AIProvider(Protocol):
    provider_name: str
    model: str
    prompt_version: str

    def investigate(
        self,
        record: NormalizedRecord,
        triggered: list[RuleEvaluation],
        issue_label: str,
        risk_score: int,
    ) -> dict:
        ...


class DisabledProvider:
    provider_name = "disabled"
    model = "none"
    prompt_version = "v0"

    def investigate(self, *args, **kwargs) -> dict:
        raise RuntimeError("Il provider AI è disabilitato")


class MockProvider:
    provider_name = "mock"
    model = "mock-payroll-ops"
    prompt_version = "case-context-v1"

    def investigate(
        self,
        record: NormalizedRecord,
        triggered: list[RuleEvaluation],
        issue_label: str,
        risk_score: int,
    ) -> dict:
        evidence: list[str] = []
        checks: list[str] = []
        summary_parts: list[str] = []
        rule_ids = {item.rule_id for item in triggered}

        def eur(value: float) -> str:
            return f"€{value:,.0f}".replace(",", ".")

        evidence.append(f"Dipendente {record.employee_id} · {record.team} · periodo {record.period}.")
        evidence.extend(item.message for item in triggered)

        if "SALARY_VARIATION" in rule_ids or "OUTSIDE_HISTORICAL_RANGE" in rule_ids:
            pct = round((record.salary_delta_ratio or 0) * 100, 1)
            sign = "+" if pct > 0 else ""
            pct_label = f"{sign}{str(pct).replace('.', ',')}%"
            summary_parts.append(
                f"La retribuzione lorda è passata da {eur(record.previous_gross_salary)} a {eur(record.gross_salary)} ({pct_label}) rispetto al periodo precedente."
            )
            evidence.append(f"La media a 6 mesi è {eur(record.avg_6m_gross)}.")
            checks.append("Verificare se una promozione o un cambio retribuzione non è stato allineato da HR.")
            checks.append("Controllare se un adeguamento una tantum è stato registrato come retribuzione base.")

        if "MISSING_SALARY_EVENT" in rule_ids:
            summary_parts.append("Nei dati HR forniti non c'è un evento di cambio retribuzione corrispondente.")
            checks.append("Chiedere a People Ops se l'evento esiste in HRIS ma è caduto nel flusso payroll.")

        if "MISSING_IBAN" in rule_ids:
            summary_parts.append("Il record è senza IBAN, quindi il pagamento non può essere disposto così com'è.")
            checks.append("Verificare la completezza dell'onboarding e chiedere i dati bancari dal canale previsto.")

        if "IMPLAUSIBLE_OVERTIME" in rule_ids:
            summary_parts.append(f"{record.overtime_hours:.0f} ore di straordinario sono fuori da un range mensile normale.")
            checks.append("Verificare i totali timesheet e se esiste un'approvazione dello straordinario.")

        if "UNUSUAL_BONUS" in rule_ids:
            summary_parts.append(f"Un bonus di {eur(record.bonus_amount)} è elevato rispetto alla retribuzione lorda.")
            checks.append("Confermare il codice motivo del bonus, la documentazione del piano o l'approvazione una tantum.")

        if "MANUAL_OVERRIDE" in rule_ids:
            summary_parts.append("È presente un override manuale: i valori vanno letti come modificati da uno specialista.")
            checks.append("Leggere la nota di override e confermare che sia ancora valida per questo periodo.")

        if "DUPLICATE_RECORD" in rule_ids:
            summary_parts.append("Questo dipendente compare più di una volta nello stesso periodo: rischio di doppio pagamento.")
            checks.append("Confrontare le due righe e tenere solo il record del sistema sorgente corretto.")

        if not summary_parts:
            summary_parts.append(f"{issue_label} è stata sollevata da controlli deterministici e richiede review dell'operatore.")

        if not checks:
            checks.append("Rivedere i controlli scattati e i campi a supporto prima di risolvere.")

        confidence = min(0.86, 0.52 + 0.08 * len(triggered))
        if "MISSING_SALARY_EVENT" in rule_ids and "SALARY_VARIATION" in rule_ids:
            confidence = 0.78

        return {
            "summary": " ".join(summary_parts),
            "evidence": evidence,
            "suggested_checks": checks,
            "confidence": round(confidence, 2),
            "limitations": [
                "Sono stati usati solo il record payroll, lo snapshot storico e il flag evento HR forniti.",
                "Questo output non approva, non rifiuta e non modifica il payroll.",
                "Non è stata inventata evidenza assente dal contesto del caso.",
            ],
            "provider": self.provider_name,
            "model": self.model,
            "prompt_version": self.prompt_version,
        }


def get_provider(name: str) -> AIProvider:
    if name == "disabled":
        return DisabledProvider()
    return MockProvider()
