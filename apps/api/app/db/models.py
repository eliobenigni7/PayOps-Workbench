from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Batch(Base):
    __tablename__ = "batches"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    period: Mapped[str] = mapped_column(String, index=True)
    source: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="processed")
    record_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    records: Mapped[list["EmployeeRecord"]] = relationship(back_populates="batch")
    exceptions: Mapped[list["ExceptionCase"]] = relationship(back_populates="batch")


class EmployeeRecord(Base):
    __tablename__ = "employee_records"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    batch_id: Mapped[str] = mapped_column(ForeignKey("batches.id"), index=True)
    employee_id: Mapped[str] = mapped_column(String, index=True)
    employee_name: Mapped[str] = mapped_column(String)
    team: Mapped[str] = mapped_column(String)
    period: Mapped[str] = mapped_column(String)
    gross_salary: Mapped[float] = mapped_column(Float)
    previous_gross_salary: Mapped[float] = mapped_column(Float)
    avg_6m_gross: Mapped[float] = mapped_column(Float)
    regular_hours: Mapped[float] = mapped_column(Float)
    overtime_hours: Mapped[float] = mapped_column(Float)
    bonus_amount: Mapped[float] = mapped_column(Float)
    iban_present: Mapped[bool] = mapped_column(Boolean)
    salary_change_event: Mapped[bool] = mapped_column(Boolean)
    manual_override: Mapped[bool] = mapped_column(Boolean)
    routing: Mapped[str] = mapped_column(String, index=True)
    raw_json: Mapped[str] = mapped_column(Text, default="{}")

    batch: Mapped[Batch] = relationship(back_populates="records")
    exceptions: Mapped[list["ExceptionCase"]] = relationship(back_populates="record")


class ExceptionCase(Base):
    __tablename__ = "exceptions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    record_id: Mapped[str] = mapped_column(ForeignKey("employee_records.id"), index=True)
    batch_id: Mapped[str] = mapped_column(ForeignKey("batches.id"), index=True)
    status: Mapped[str] = mapped_column(String, index=True)
    priority: Mapped[str] = mapped_column(String, index=True)
    risk_score: Mapped[int] = mapped_column(Integer)
    financial_exposure: Mapped[float] = mapped_column(Float)
    issue_type: Mapped[str] = mapped_column(String, index=True)
    issue_label: Mapped[str] = mapped_column(String)
    assigned_to: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, index=True)

    batch: Mapped[Batch] = relationship(back_populates="exceptions")
    record: Mapped[EmployeeRecord] = relationship(back_populates="exceptions")
    rule_results: Mapped[list["RuleResult"]] = relationship(back_populates="exception")
    breakdown: Mapped[list["PriorityBreakdown"]] = relationship(back_populates="exception")
    resolution: Mapped["ReviewResolution | None"] = relationship(back_populates="exception")
    investigations: Mapped[list["AIInvestigation"]] = relationship(back_populates="exception")


class RuleResult(Base):
    __tablename__ = "rule_results"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    exception_id: Mapped[str] = mapped_column(ForeignKey("exceptions.id"), index=True)
    record_id: Mapped[str] = mapped_column(String, index=True)
    rule_id: Mapped[str] = mapped_column(String)
    triggered: Mapped[bool] = mapped_column(Boolean)
    severity: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(Text)
    issue_type: Mapped[str] = mapped_column(String)
    evidence_json: Mapped[str] = mapped_column(Text, default="{}")

    exception: Mapped[ExceptionCase] = relationship(back_populates="rule_results")


class PriorityBreakdown(Base):
    __tablename__ = "priority_breakdowns"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    exception_id: Mapped[str] = mapped_column(ForeignKey("exceptions.id"), index=True)
    component: Mapped[str] = mapped_column(String)
    value: Mapped[int] = mapped_column(Integer)
    explanation: Mapped[str] = mapped_column(Text)

    exception: Mapped[ExceptionCase] = relationship(back_populates="breakdown")


class ReviewResolution(Base):
    __tablename__ = "review_resolutions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    exception_id: Mapped[str] = mapped_column(ForeignKey("exceptions.id"), unique=True)
    outcome: Mapped[str] = mapped_column(String)
    reason_code: Mapped[str] = mapped_column(String)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_by: Mapped[str] = mapped_column(String)
    resolved_at: Mapped[datetime] = mapped_column(DateTime)
    handling_minutes: Mapped[float] = mapped_column(Float)

    exception: Mapped[ExceptionCase] = relationship(back_populates="resolution")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    entity_type: Mapped[str] = mapped_column(String, index=True)
    entity_id: Mapped[str] = mapped_column(String, index=True)
    event_type: Mapped[str] = mapped_column(String)
    payload_json: Mapped[str] = mapped_column(Text, default="{}")
    actor: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime)


class AIInvestigation(Base):
    __tablename__ = "ai_investigations"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    exception_id: Mapped[str] = mapped_column(ForeignKey("exceptions.id"), index=True)
    summary: Mapped[str] = mapped_column(Text)
    evidence_json: Mapped[str] = mapped_column(Text)
    suggested_checks_json: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    limitations_json: Mapped[str] = mapped_column(Text)
    provider: Mapped[str] = mapped_column(String)
    model: Mapped[str] = mapped_column(String)
    prompt_version: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime)

    exception: Mapped[ExceptionCase] = relationship(back_populates="investigations")


class ImprovementOpportunity(Base):
    __tablename__ = "improvement_opportunities"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    issue_type: Mapped[str] = mapped_column(String, unique=True, index=True)
    title: Mapped[str] = mapped_column(String)
    monthly_occurrences: Mapped[int] = mapped_column(Integer)
    avg_handling_minutes: Mapped[float] = mapped_column(Float)
    monthly_effort_hours: Mapped[float] = mapped_column(Float)
    false_positive_rate: Mapped[float] = mapped_column(Float, default=0)
    trend: Mapped[str] = mapped_column(String, default="stable")
    root_cause_hypothesis: Mapped[str] = mapped_column(Text)
    suggested_intervention: Mapped[str] = mapped_column(Text)
    implementation_effort: Mapped[str] = mapped_column(String)
    expected_impact: Mapped[str] = mapped_column(Text)
    measurement_kpis_json: Mapped[str] = mapped_column(Text)
    expected_effort_removed_hours: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String, default="detected")
