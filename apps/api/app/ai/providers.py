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
        raise RuntimeError("AI provider is disabled")


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

        evidence.append(f"Employee {record.employee_id} · {record.team} · period {record.period}.")
        evidence.extend(item.message for item in triggered)

        if "SALARY_VARIATION" in rule_ids or "OUTSIDE_HISTORICAL_RANGE" in rule_ids:
            pct = round((record.salary_delta_ratio or 0) * 100, 1)
            summary_parts.append(
                f"Gross salary moved from €{record.previous_gross_salary:,.0f} to €{record.gross_salary:,.0f} ({pct:+.1f}%) versus the previous period."
            )
            evidence.append(f"6-month average is €{record.avg_6m_gross:,.0f}.")
            checks.append("Confirm whether a promotion or compensation change was not synced from HR.")
            checks.append("Check whether a one-off adjustment was coded as base salary.")

        if "MISSING_SALARY_EVENT" in rule_ids:
            summary_parts.append("No corresponding salary-change event is present in the provided HR data.")
            checks.append("Ask People Ops whether the event exists in the HRIS but was dropped from the payroll feed.")

        if "MISSING_IBAN" in rule_ids:
            summary_parts.append("The record has no IBAN, so the payment cannot be released as-is.")
            checks.append("Check onboarding completeness and ask the employee to provide bank details through the usual channel.")

        if "IMPLAUSIBLE_OVERTIME" in rule_ids:
            summary_parts.append(f"{record.overtime_hours:.0f} overtime hours is outside a normal monthly range.")
            checks.append("Verify timesheet totals and whether an overtime approval exists.")

        if "UNUSUAL_BONUS" in rule_ids:
            summary_parts.append(f"A bonus of €{record.bonus_amount:,.0f} is large relative to gross pay.")
            checks.append("Confirm the bonus reason code, plan documentation, or one-off approval.")

        if "MANUAL_OVERRIDE" in rule_ids:
            summary_parts.append("A manual override is present, so the values should be read as specialist-edited.")
            checks.append("Read the override note and confirm it is still valid for this period.")

        if "DUPLICATE_RECORD" in rule_ids:
            summary_parts.append("This employee appears more than once in the same period, which can create a duplicate payment.")
            checks.append("Compare both rows and keep only the intended source-system record.")

        if not summary_parts:
            summary_parts.append(f"{issue_label} was raised by deterministic checks and needs operator review.")

        if not checks:
            checks.append("Review the triggered checks and supporting fields before resolving.")

        confidence = min(0.86, 0.52 + 0.08 * len(triggered))
        if "MISSING_SALARY_EVENT" in rule_ids and "SALARY_VARIATION" in rule_ids:
            confidence = 0.78

        return {
            "summary": " ".join(summary_parts),
            "evidence": evidence,
            "suggested_checks": checks,
            "confidence": round(confidence, 2),
            "limitations": [
                "Only the provided payroll record, history snapshot and HR event flag were used.",
                "This output does not approve, reject, or change payroll.",
                "Evidence not present in the case context was not invented.",
            ],
            "provider": self.provider_name,
            "model": self.model,
            "prompt_version": self.prompt_version,
        }


def get_provider(name: str) -> AIProvider:
    if name == "disabled":
        return DisabledProvider()
    return MockProvider()
