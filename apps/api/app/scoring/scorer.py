from __future__ import annotations

from app.domain.enums import ISSUE_LABELS, RULE_LABELS, SEVERITY_LABELS, SEVERITY_RANK, IssueType, Priority, Routing, Severity
from app.domain.types import NormalizedRecord, PriorityComponent, RoutingDecision, RuleEvaluation

SEVERITY_POINTS = {
    Severity.CRITICAL: 40,
    Severity.HIGH: 28,
    Severity.MEDIUM: 16,
    Severity.LOW: 8,
}

HIGH_CONFIDENCE_RULES = {"MISSING_IBAN", "DUPLICATE_RECORD", "MANUAL_OVERRIDE"}


def financial_exposure(record: NormalizedRecord, triggered: list[RuleEvaluation]) -> float:
    types = {item.issue_type for item in triggered}
    exposure = 0.0
    if IssueType.SALARY_DISCREPANCY in types or IssueType.MISSING_HR_EVENT in types:
        exposure += abs(record.salary_delta)
    if IssueType.BONUS_ANOMALY in types:
        exposure += record.bonus_amount
    if IssueType.OVERTIME_ISSUE in types:
        hourly = record.gross_salary / max(record.regular_hours, 1)
        exposure += record.overtime_hours * hourly
    if IssueType.MISSING_BANK_INFORMATION in types:
        exposure += record.gross_salary
    if IssueType.DUPLICATE_RECORD in types:
        exposure += record.gross_salary + record.bonus_amount
    if IssueType.MANUAL_OVERRIDE in types and exposure == 0:
        exposure += abs(record.salary_delta) or record.bonus_amount
    return round(exposure, 2)


def _exposure_points(amount: float) -> int:
    if amount >= 1800:
        return 25
    if amount >= 1000:
        return 20
    if amount >= 400:
        return 14
    if amount >= 100:
        return 8
    return 4


def _confidence_points(triggered: list[RuleEvaluation]) -> int:
    if any(item.rule_id in HIGH_CONFIDENCE_RULES for item in triggered):
        return 20
    if len(triggered) >= 3:
        return 20
    if len(triggered) == 2:
        return 16
    return 12


def _missing_event_points(triggered: list[RuleEvaluation]) -> int:
    return 15 if any(item.rule_id == "MISSING_SALARY_EVENT" for item in triggered) else 0


def _primary_issue(triggered: list[RuleEvaluation]) -> RuleEvaluation:
    return sorted(
        triggered,
        key=lambda item: (SEVERITY_RANK[item.severity], item.rule_id),
        reverse=True,
    )[0]


def _priority_for_score(score: int) -> Priority:
    if score >= 80:
        return Priority.CRITICAL
    if score >= 55:
        return Priority.HIGH
    if score >= 35:
        return Priority.MEDIUM
    return Priority.LOW


def score_record(record: NormalizedRecord, evaluations: list[RuleEvaluation]) -> RoutingDecision:
    triggered = [item for item in evaluations if item.triggered]
    if not triggered:
        return RoutingDecision(routing=Routing.AUTO_CLEARED, triggered_rules=[])

    highest = max(triggered, key=lambda item: SEVERITY_RANK[item.severity])
    severity_pts = SEVERITY_POINTS[highest.severity]
    exposure = financial_exposure(record, triggered)
    exposure_pts = _exposure_points(exposure)
    confidence_pts = _confidence_points(triggered)
    missing_pts = _missing_event_points(triggered)

    raw_total = severity_pts + exposure_pts + confidence_pts + missing_pts
    if raw_total > 100:
        confidence_pts = max(8, confidence_pts - (raw_total - 100))
    total = severity_pts + exposure_pts + confidence_pts + missing_pts

    primary = _primary_issue(triggered)
    breakdown = [
        PriorityComponent(
            component="severity",
            value=severity_pts,
            explanation=f"Il controllo con gravità più alta è {RULE_LABELS.get(highest.rule_id, highest.rule_id)} ({SEVERITY_LABELS[highest.severity]}).",
        ),
        PriorityComponent(
            component="financial_exposure",
            value=exposure_pts,
            explanation=f"L'importo a rischio stimato è €{exposure:,.0f}.".replace(",", "."),
        ),
        PriorityComponent(
            component="rule_confidence",
            value=confidence_pts,
            explanation="Controlli deterministici con soglie esplicite; la confidenza sale quando più regole concordano.",
        ),
        PriorityComponent(
            component="missing_support_event",
            value=missing_pts,
            explanation=(
                "Nessun evento HR a supporto di una variazione retributiva rilevante."
                if missing_pts
                else "Nessuna penalità per evento di supporto mancante."
            ),
        ),
    ]

    return RoutingDecision(
        routing=Routing.NEEDS_REVIEW,
        priority=_priority_for_score(total),
        risk_score=total,
        financial_exposure=exposure,
        issue_type=primary.issue_type,
        issue_label=ISSUE_LABELS[primary.issue_type],
        breakdown=breakdown,
        triggered_rules=triggered,
    )
