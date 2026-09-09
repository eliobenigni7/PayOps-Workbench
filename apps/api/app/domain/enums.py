from enum import StrEnum


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Priority(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Routing(StrEnum):
    AUTO_CLEARED = "auto_cleared"
    NEEDS_REVIEW = "needs_review"
    EVALUATION_FAILED = "evaluation_failed"


class ExceptionStatus(StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"
    REQUESTED_INFO = "requested_info"
    ESCALATED = "escalated"


class IssueType(StrEnum):
    MISSING_BANK_INFORMATION = "missing_bank_information"
    SALARY_DISCREPANCY = "salary_discrepancy"
    MISSING_HR_EVENT = "missing_hr_event"
    OVERTIME_ISSUE = "overtime_issue"
    BONUS_ANOMALY = "bonus_anomaly"
    MANUAL_OVERRIDE = "manual_override"
    DUPLICATE_RECORD = "duplicate_record"


class ResolutionOutcome(StrEnum):
    CONFIRM_ISSUE = "confirm_issue"
    MARK_EXPECTED = "mark_expected"
    REQUEST_INFO = "request_info"
    ESCALATE = "escalate"


class ReasonCode(StrEnum):
    SALARY_INCREASE = "salary_increase"
    ONE_OFF_BONUS = "one_off_bonus"
    MANUAL_ADJUSTMENT = "manual_adjustment"
    DATA_CORRECTION = "data_correction"
    MISSING_SOURCE_DATA = "missing_source_data"
    PROCESS_GAP = "process_gap"
    DUPLICATE_PAYMENT = "duplicate_payment"
    LEGITIMATE_OVERTIME = "legitimate_overtime"
    ONBOARDING_INCOMPLETE = "onboarding_incomplete"
    OTHER = "other"


class ImprovementStatus(StrEnum):
    DETECTED = "detected"
    INVESTIGATE = "investigate"
    PLANNED = "planned"
    IMPLEMENTED = "implemented"
    DISMISSED = "dismissed"


class ImplementationEffort(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


ISSUE_LABELS: dict[IssueType, str] = {
    IssueType.MISSING_BANK_INFORMATION: "Missing bank information",
    IssueType.SALARY_DISCREPANCY: "Salary anomaly",
    IssueType.MISSING_HR_EVENT: "Missing HR event",
    IssueType.OVERTIME_ISSUE: "Implausible overtime",
    IssueType.BONUS_ANOMALY: "Bonus anomaly",
    IssueType.MANUAL_OVERRIDE: "Manual override",
    IssueType.DUPLICATE_RECORD: "Duplicate record",
}

REASON_LABELS: dict[ReasonCode, str] = {
    ReasonCode.SALARY_INCREASE: "Salary increase",
    ReasonCode.ONE_OFF_BONUS: "One-off bonus",
    ReasonCode.MANUAL_ADJUSTMENT: "Manual adjustment",
    ReasonCode.DATA_CORRECTION: "Data correction",
    ReasonCode.MISSING_SOURCE_DATA: "Missing source data",
    ReasonCode.PROCESS_GAP: "Process gap",
    ReasonCode.DUPLICATE_PAYMENT: "Duplicate payment",
    ReasonCode.LEGITIMATE_OVERTIME: "Legitimate overtime",
    ReasonCode.ONBOARDING_INCOMPLETE: "Onboarding incomplete",
    ReasonCode.OTHER: "Other",
}

OUTCOME_LABELS: dict[ResolutionOutcome, str] = {
    ResolutionOutcome.CONFIRM_ISSUE: "Confirm issue",
    ResolutionOutcome.MARK_EXPECTED: "Mark as expected",
    ResolutionOutcome.REQUEST_INFO: "Request information",
    ResolutionOutcome.ESCALATE: "Escalate",
}

SEVERITY_RANK = {
    Severity.LOW: 1,
    Severity.MEDIUM: 2,
    Severity.HIGH: 3,
    Severity.CRITICAL: 4,
}
