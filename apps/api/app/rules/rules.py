from __future__ import annotations

from collections.abc import Callable

from app.domain.enums import IssueType, Severity
from app.domain.types import NormalizedRecord, RuleEvaluation

RuleFn = Callable[[NormalizedRecord], RuleEvaluation]


def _pct(value: float | None) -> float | None:
    if value is None:
        return None
    return round(value * 100, 1)


def missing_iban(record: NormalizedRecord) -> RuleEvaluation:
    triggered = not record.iban_present
    return RuleEvaluation(
        rule_id="MISSING_IBAN",
        triggered=triggered,
        severity=Severity.HIGH,
        issue_type=IssueType.MISSING_BANK_INFORMATION,
        message="Bank details are missing — payment cannot be released without an IBAN.",
        evidence={"iban_present": record.iban_present},
    )


def salary_variation(record: NormalizedRecord) -> RuleEvaluation:
    ratio = record.salary_delta_ratio
    triggered = ratio is not None and ratio >= 0.30
    severity = Severity.CRITICAL if (ratio or 0) >= 0.40 else Severity.HIGH
    pct = _pct(ratio)
    direction = "increased" if record.salary_delta > 0 else "decreased"
    message = (
        f"Gross salary {direction} {pct}% versus the previous period."
        if triggered
        else "Salary variation is within the 30% review threshold."
    )
    return RuleEvaluation(
        rule_id="SALARY_VARIATION",
        triggered=triggered,
        severity=severity,
        issue_type=IssueType.SALARY_DISCREPANCY,
        message=message,
        evidence={
            "gross_salary": record.gross_salary,
            "previous_gross_salary": record.previous_gross_salary,
            "delta": round(record.salary_delta, 2),
            "delta_pct": pct,
            "threshold_pct": 30,
        },
    )


def missing_salary_event(record: NormalizedRecord) -> RuleEvaluation:
    ratio = record.salary_delta_ratio
    triggered = ratio is not None and ratio >= 0.10 and not record.salary_change_event
    severity = Severity.HIGH if (ratio or 0) >= 0.30 else Severity.MEDIUM
    return RuleEvaluation(
        rule_id="MISSING_SALARY_EVENT",
        triggered=triggered,
        severity=severity,
        issue_type=IssueType.MISSING_HR_EVENT,
        message=(
            "No salary-change HR event found to support the pay change."
            if triggered
            else "Salary change is supported by an HR event or is within tolerance."
        ),
        evidence={
            "salary_change_event": record.salary_change_event,
            "delta_pct": _pct(ratio),
            "threshold_pct": 10,
        },
    )


def outside_historical_range(record: NormalizedRecord) -> RuleEvaluation:
    ratio = record.historical_delta_ratio
    triggered = ratio is not None and ratio >= 0.25
    severity = Severity.HIGH if (ratio or 0) >= 0.35 else Severity.MEDIUM
    pct = _pct(ratio)
    return RuleEvaluation(
        rule_id="OUTSIDE_HISTORICAL_RANGE",
        triggered=triggered,
        severity=severity,
        issue_type=IssueType.SALARY_DISCREPANCY,
        message=(
            f"Gross pay is {pct}% away from the 6-month average."
            if triggered
            else "Gross pay is within the 6-month historical range."
        ),
        evidence={
            "gross_salary": record.gross_salary,
            "avg_6m_gross": record.avg_6m_gross,
            "delta_pct": pct,
            "threshold_pct": 25,
        },
    )


def implausible_overtime(record: NormalizedRecord) -> RuleEvaluation:
    hours = record.overtime_hours
    triggered = hours > 20
    if hours >= 40:
        severity = Severity.CRITICAL
    elif hours >= 28:
        severity = Severity.HIGH
    else:
        severity = Severity.MEDIUM
    return RuleEvaluation(
        rule_id="IMPLAUSIBLE_OVERTIME",
        triggered=triggered,
        severity=severity,
        issue_type=IssueType.OVERTIME_ISSUE,
        message=(
            f"{hours:.0f} overtime hours is implausible for a standard monthly period."
            if triggered
            else "Overtime hours are within the expected range."
        ),
        evidence={"overtime_hours": hours, "threshold_hours": 20},
    )


def unusual_bonus(record: NormalizedRecord) -> RuleEvaluation:
    bonus = record.bonus_amount
    ratio = bonus / record.gross_salary if record.gross_salary else 0
    triggered = bonus > 0 and (bonus >= 1500 or ratio >= 0.40)
    severity = Severity.HIGH if bonus >= 2000 else Severity.MEDIUM
    return RuleEvaluation(
        rule_id="UNUSUAL_BONUS",
        triggered=triggered,
        severity=severity,
        issue_type=IssueType.BONUS_ANOMALY,
        message=(
            f"Bonus of €{bonus:,.0f} is unusually high relative to gross pay."
            if triggered
            else "Bonus amount is within expected bounds."
        ),
        evidence={
            "bonus_amount": bonus,
            "gross_salary": record.gross_salary,
            "bonus_to_gross_pct": round(ratio * 100, 1),
        },
    )


def manual_override(record: NormalizedRecord) -> RuleEvaluation:
    triggered = record.manual_override
    return RuleEvaluation(
        rule_id="MANUAL_OVERRIDE",
        triggered=triggered,
        severity=Severity.MEDIUM,
        issue_type=IssueType.MANUAL_OVERRIDE,
        message=(
            "Record includes a manual override and requires specialist review."
            if triggered
            else "No manual override flag."
        ),
        evidence={"manual_override": record.manual_override},
    )


def duplicate_record(record: NormalizedRecord) -> RuleEvaluation:
    triggered = record.is_duplicate
    return RuleEvaluation(
        rule_id="DUPLICATE_RECORD",
        triggered=triggered,
        severity=Severity.CRITICAL,
        issue_type=IssueType.DUPLICATE_RECORD,
        message=(
            "Duplicate employee/period record in this batch."
            if triggered
            else "Employee/period combination is unique in this batch."
        ),
        evidence={"duplicate_count": record.duplicate_count},
    )


RULES: tuple[RuleFn, ...] = (
    missing_iban,
    salary_variation,
    missing_salary_event,
    outside_historical_range,
    implausible_overtime,
    unusual_bonus,
    manual_override,
    duplicate_record,
)

RULES_BY_ID: dict[str, RuleFn] = {
    "MISSING_IBAN": missing_iban,
    "SALARY_VARIATION": salary_variation,
    "MISSING_SALARY_EVENT": missing_salary_event,
    "OUTSIDE_HISTORICAL_RANGE": outside_historical_range,
    "IMPLAUSIBLE_OVERTIME": implausible_overtime,
    "UNUSUAL_BONUS": unusual_bonus,
    "MANUAL_OVERRIDE": manual_override,
    "DUPLICATE_RECORD": duplicate_record,
}
