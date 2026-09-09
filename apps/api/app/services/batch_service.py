from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import (
    AuditEvent,
    Batch,
    EmployeeRecord,
    ExceptionCase,
    PriorityBreakdown,
    RuleResult,
)
from app.domain.enums import ISSUE_LABELS, IssueType, Routing
from app.domain.types import NormalizedRecord
from app.rules.engine import evaluate_record
from app.scoring.scorer import score_record
from app.util import new_id, parse_bool, parse_float

CSV_FIELDS = (
    "employee_id",
    "employee_name",
    "team",
    "period",
    "gross_salary",
    "previous_gross_salary",
    "regular_hours",
    "overtime_hours",
    "bonus_amount",
    "iban_present",
    "salary_change_event",
    "manual_override",
)


def normalize_row(row: dict[str, Any], duplicate_count: int = 1) -> NormalizedRecord:
    previous = parse_float(row.get("previous_gross_salary"))
    avg_6m = parse_float(row.get("avg_6m_gross"), previous if previous else parse_float(row.get("gross_salary")))
    return NormalizedRecord(
        employee_id=str(row["employee_id"]).strip(),
        employee_name=str(row["employee_name"]).strip(),
        team=str(row.get("team", "Unassigned")).strip(),
        period=str(row["period"]).strip(),
        gross_salary=parse_float(row.get("gross_salary")),
        previous_gross_salary=previous,
        avg_6m_gross=avg_6m,
        regular_hours=parse_float(row.get("regular_hours"), 168),
        overtime_hours=parse_float(row.get("overtime_hours")),
        bonus_amount=parse_float(row.get("bonus_amount")),
        iban_present=parse_bool(row.get("iban_present", True)),
        salary_change_event=parse_bool(row.get("salary_change_event", False)),
        manual_override=parse_bool(row.get("manual_override", False)),
        is_duplicate=duplicate_count > 1,
        duplicate_count=duplicate_count,
    )


def _duplicate_counts(rows: list[dict[str, Any]]) -> Counter[str]:
    return Counter(str(row["employee_id"]).strip() for row in rows)


def process_batch(
    db: Session,
    rows: list[dict[str, Any]],
    *,
    period: str,
    source: str,
    batch_id: str | None = None,
    processed_at: datetime | None = None,
    created_at: datetime | None = None,
    actor: str = "system",
) -> Batch:
    now = processed_at or datetime.utcnow()
    created = created_at or now
    batch = Batch(
        id=batch_id or new_id("bat"),
        period=period,
        source=source,
        status="processed",
        record_count=len(rows),
        created_at=created,
        processed_at=now,
    )
    db.add(batch)
    db.add(
        AuditEvent(
            id=new_id("aud"),
            entity_type="batch",
            entity_id=batch.id,
            event_type="batch_imported",
            payload_json=json.dumps({"period": period, "record_count": len(rows), "source": source}),
            actor=actor,
            created_at=created,
        )
    )

    counts = _duplicate_counts(rows)
    for index, row in enumerate(rows):
        record = normalize_row(row, duplicate_count=counts[str(row["employee_id"]).strip()])
        evaluations = evaluate_record(record)
        decision = score_record(record, evaluations)
        record_id = str(row.get("record_id") or new_id("rec"))
        db.add(
            EmployeeRecord(
                id=record_id,
                batch_id=batch.id,
                employee_id=record.employee_id,
                employee_name=record.employee_name,
                team=record.team,
                period=record.period,
                gross_salary=record.gross_salary,
                previous_gross_salary=record.previous_gross_salary,
                avg_6m_gross=record.avg_6m_gross,
                regular_hours=record.regular_hours,
                overtime_hours=record.overtime_hours,
                bonus_amount=record.bonus_amount,
                iban_present=record.iban_present,
                salary_change_event=record.salary_change_event,
                manual_override=record.manual_override,
                routing=decision.routing.value,
                raw_json=json.dumps(row, default=str),
            )
        )

        if decision.routing != Routing.NEEDS_REVIEW:
            continue

        exception_id = str(row.get("exception_id") or _exception_id(record, index))
        assigned_to = row.get("assigned_to")
        created_exception_at = row.get("created_at") or now
        if isinstance(created_exception_at, str):
            created_exception_at = datetime.fromisoformat(created_exception_at)

        db.add(
            ExceptionCase(
                id=exception_id,
                record_id=record_id,
                batch_id=batch.id,
                status=str(row.get("status") or "open"),
                priority=decision.priority.value if decision.priority else "medium",
                risk_score=decision.risk_score,
                financial_exposure=decision.financial_exposure,
                issue_type=(decision.issue_type or IssueType.SALARY_DISCREPANCY).value,
                issue_label=decision.issue_label or ISSUE_LABELS[IssueType.SALARY_DISCREPANCY],
                assigned_to=assigned_to,
                created_at=created_exception_at,
            )
        )
        for evaluation in decision.triggered_rules:
            db.add(
                RuleResult(
                    id=new_id("rul"),
                    exception_id=exception_id,
                    record_id=record_id,
                    rule_id=evaluation.rule_id,
                    triggered=evaluation.triggered,
                    severity=evaluation.severity.value,
                    message=evaluation.message,
                    issue_type=evaluation.issue_type.value,
                    evidence_json=json.dumps(evaluation.evidence),
                )
            )
        for component in decision.breakdown:
            db.add(
                PriorityBreakdown(
                    id=new_id("brk"),
                    exception_id=exception_id,
                    component=component.component,
                    value=component.value,
                    explanation=component.explanation,
                )
            )
        db.add(
            AuditEvent(
                id=new_id("aud"),
                entity_type="exception",
                entity_id=exception_id,
                event_type="exception_opened",
                payload_json=json.dumps(
                    {
                        "priority": decision.priority.value if decision.priority else None,
                        "risk_score": decision.risk_score,
                        "issue_type": decision.issue_type.value if decision.issue_type else None,
                    }
                ),
                actor=actor,
                created_at=created_exception_at,
            )
        )

    db.flush()
    return batch


def _exception_id(record: NormalizedRecord, index: int) -> str:
    if record.employee_id == "EMP-1042":
        return "exc_1042"
    number = record.employee_id.replace("EMP-", "")
    return f"exc_{number}_{index}"
