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
    IssueType.MISSING_BANK_INFORMATION: "IBAN mancante",
    IssueType.SALARY_DISCREPANCY: "Anomalia retributiva",
    IssueType.MISSING_HR_EVENT: "Evento HR mancante",
    IssueType.OVERTIME_ISSUE: "Straordinario implausibile",
    IssueType.BONUS_ANOMALY: "Anomalia sul bonus",
    IssueType.MANUAL_OVERRIDE: "Override manuale",
    IssueType.DUPLICATE_RECORD: "Record duplicato",
}

REASON_LABELS: dict[ReasonCode, str] = {
    ReasonCode.SALARY_INCREASE: "Aumento retributivo",
    ReasonCode.ONE_OFF_BONUS: "Bonus una tantum",
    ReasonCode.MANUAL_ADJUSTMENT: "Rettifica manuale",
    ReasonCode.DATA_CORRECTION: "Correzione dati",
    ReasonCode.MISSING_SOURCE_DATA: "Dato sorgente mancante",
    ReasonCode.PROCESS_GAP: "Gap di processo",
    ReasonCode.DUPLICATE_PAYMENT: "Pagamento duplicato",
    ReasonCode.LEGITIMATE_OVERTIME: "Straordinario legittimo",
    ReasonCode.ONBOARDING_INCOMPLETE: "Onboarding incompleto",
    ReasonCode.OTHER: "Altro",
}

OUTCOME_LABELS: dict[ResolutionOutcome, str] = {
    ResolutionOutcome.CONFIRM_ISSUE: "Conferma anomalia",
    ResolutionOutcome.MARK_EXPECTED: "Segna come atteso",
    ResolutionOutcome.REQUEST_INFO: "Richiedi informazioni",
    ResolutionOutcome.ESCALATE: "Scala",
}

SEVERITY_LABELS = {
    Severity.CRITICAL: "critico",
    Severity.HIGH: "alto",
    Severity.MEDIUM: "medio",
    Severity.LOW: "basso",
}

RULE_LABELS = {
    "MISSING_IBAN": "IBAN mancante",
    "SALARY_VARIATION": "Variazione retribuzione",
    "MISSING_SALARY_EVENT": "Evento retribuzione mancante",
    "OUTSIDE_HISTORICAL_RANGE": "Fuori range storico",
    "IMPLAUSIBLE_OVERTIME": "Straordinario implausibile",
    "UNUSUAL_BONUS": "Bonus anomalo",
    "MANUAL_OVERRIDE": "Override manuale",
    "DUPLICATE_RECORD": "Record duplicato",
}

EFFORT_LABELS = {
    "low": "basso",
    "medium": "medio",
    "high": "alto",
}

SEVERITY_RANK = {
    Severity.LOW: 1,
    Severity.MEDIUM: 2,
    Severity.HIGH: 3,
    Severity.CRITICAL: 4,
}
