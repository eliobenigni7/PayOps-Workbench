from __future__ import annotations

from dataclasses import dataclass

from app.domain.enums import IssueType


@dataclass(frozen=True)
class IssuePlaybook:
    title: str
    hypothesis: str
    intervention: str
    effort: str
    impact: str
    kpis: tuple[str, ...]
    prevention_rate: float
    default_handling_minutes: float


PLAYBOOKS: dict[IssueType, IssuePlaybook] = {
    IssueType.MISSING_BANK_INFORMATION: IssuePlaybook(
        title="Missing bank information",
        hypothesis="Bank information is not mandatory at the point where employee onboarding is completed.",
        intervention="Add completeness validation before onboarding can be marked complete.",
        effort="low",
        impact="Reduce downstream bank-data exceptions by 70–90%.",
        kpis=("monthly exception count", "average handling time", "onboarding completion rate"),
        prevention_rate=0.8,
        default_handling_minutes=6.2,
    ),
    IssueType.SALARY_DISCREPANCY: IssuePlaybook(
        title="Salary change without a complete audit trail",
        hypothesis="Compensation changes reach payroll before the matching HR event is written back.",
        intervention="Block payroll close when a >10% salary change has no linked HR event.",
        effort="medium",
        impact="Cut salary-anomaly reviews by catching missing events at source.",
        kpis=("salary exception count", "missing-event rate", "time to first review"),
        prevention_rate=0.55,
        default_handling_minutes=8.4,
    ),
    IssueType.MISSING_HR_EVENT: IssuePlaybook(
        title="Pay changes missing supporting HR events",
        hypothesis="HR and payroll systems do not share a required event contract for compensation changes.",
        intervention="Make the salary-change event a required field in the HR export used for payroll.",
        effort="medium",
        impact="Give operators evidence instead of reconstructing intent from numbers.",
        kpis=("missing-event exceptions", "false-positive rate", "average handling time"),
        prevention_rate=0.7,
        default_handling_minutes=7.8,
    ),
    IssueType.BONUS_ANOMALY: IssuePlaybook(
        title="One-off bonuses without a supporting reason code",
        hypothesis="Bonus payments can be keyed without a structured reason, so unusual amounts look identical to errors.",
        intervention="Require a bonus reason code and manager confirmation above a threshold.",
        effort="low",
        impact="Let expected bonuses auto-clear while keeping true anomalies in queue.",
        kpis=("bonus exception volume", "marked-as-expected rate", "manual handling hours"),
        prevention_rate=0.6,
        default_handling_minutes=7.0,
    ),
    IssueType.OVERTIME_ISSUE: IssuePlaybook(
        title="Implausible overtime entries",
        hypothesis="Overtime is entered as a free number with no calendar or approval check.",
        intervention="Cap overtime entry at 20 hours unless an approved exception ticket is attached.",
        effort="low",
        impact="Stop extreme overtime values from reaching payroll review.",
        kpis=("overtime exception count", "hours above cap", "approval cycle time"),
        prevention_rate=0.75,
        default_handling_minutes=5.5,
    ),
    IssueType.MANUAL_OVERRIDE: IssuePlaybook(
        title="Unstructured manual overrides",
        hypothesis="Overrides are used as a workaround and rarely carry a reusable reason.",
        intervention="Replace free-text overrides with a short controlled list and expiry date.",
        effort="medium",
        impact="Turn override volume into a measurable process signal instead of hidden work.",
        kpis=("override count", "repeat employees", "reason-code completeness"),
        prevention_rate=0.4,
        default_handling_minutes=4.8,
    ),
    IssueType.DUPLICATE_RECORD: IssuePlaybook(
        title="Duplicate employee/period rows",
        hypothesis="Feeds from two source systems are concatenated without a unique employee-period key.",
        intervention="Enforce a unique employee + period constraint before the batch is accepted.",
        effort="low",
        impact="Eliminate duplicate-pay risk at ingest instead of during specialist review.",
        kpis=("duplicate count", "ingest rejection rate", "financial exposure avoided"),
        prevention_rate=0.95,
        default_handling_minutes=9.0,
    ),
}

BASELINE_REVIEW_SECONDS = 20.25
OPERATORS = ("Sofia Bianchi", "Paolo Ricci", "Giulia Neri")
