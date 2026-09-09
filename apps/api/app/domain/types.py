from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.enums import IssueType, Priority, Routing, Severity


class NormalizedRecord(BaseModel):
    employee_id: str
    employee_name: str
    team: str
    period: str
    gross_salary: float
    previous_gross_salary: float
    avg_6m_gross: float
    regular_hours: float
    overtime_hours: float
    bonus_amount: float
    iban_present: bool
    salary_change_event: bool
    manual_override: bool
    is_duplicate: bool = False
    duplicate_count: int = 1

    @property
    def salary_delta(self) -> float:
        return self.gross_salary - self.previous_gross_salary

    @property
    def salary_delta_ratio(self) -> float | None:
        if self.previous_gross_salary <= 0:
            return None
        return abs(self.salary_delta) / self.previous_gross_salary

    @property
    def historical_delta_ratio(self) -> float | None:
        if self.avg_6m_gross <= 0:
            return None
        return abs(self.gross_salary - self.avg_6m_gross) / self.avg_6m_gross


class RuleEvaluation(BaseModel):
    rule_id: str
    triggered: bool
    severity: Severity
    message: str
    issue_type: IssueType
    evidence: dict[str, object] = Field(default_factory=dict)


class PriorityComponent(BaseModel):
    component: str
    value: int
    explanation: str


class RoutingDecision(BaseModel):
    routing: Routing
    priority: Priority | None = None
    risk_score: int = 0
    financial_exposure: float = 0
    issue_type: IssueType | None = None
    issue_label: str | None = None
    breakdown: list[PriorityComponent] = Field(default_factory=list)
    triggered_rules: list[RuleEvaluation] = Field(default_factory=list)
    evaluation_error: str | None = None
