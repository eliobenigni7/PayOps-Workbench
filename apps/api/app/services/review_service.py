from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import AuditEvent, ExceptionCase, ReviewResolution
from app.domain.enums import ExceptionStatus, ReasonCode, ResolutionOutcome
from app.util import new_id

OUTCOME_STATUS = {
    ResolutionOutcome.CONFIRM_ISSUE: ExceptionStatus.RESOLVED,
    ResolutionOutcome.MARK_EXPECTED: ExceptionStatus.RESOLVED,
    ResolutionOutcome.REQUEST_INFO: ExceptionStatus.REQUESTED_INFO,
    ResolutionOutcome.ESCALATE: ExceptionStatus.ESCALATED,
}


class ReviewError(Exception):
    pass


def get_exception(db: Session, exception_id: str) -> ExceptionCase | None:
    return db.scalar(
        select(ExceptionCase)
        .options(
            selectinload(ExceptionCase.record),
            selectinload(ExceptionCase.rule_results),
            selectinload(ExceptionCase.breakdown),
            selectinload(ExceptionCase.resolution),
            selectinload(ExceptionCase.investigations),
            selectinload(ExceptionCase.batch),
        )
        .where(ExceptionCase.id == exception_id)
    )


def list_exceptions(
    db: Session,
    *,
    batch_id: str | None = None,
    priority: str | None = None,
    issue_type: str | None = None,
    assignee: str | None = None,
    status: str | None = None,
    search: str | None = None,
) -> list[ExceptionCase]:
    stmt = (
        select(ExceptionCase)
        .options(selectinload(ExceptionCase.record), selectinload(ExceptionCase.investigations))
        .order_by(ExceptionCase.risk_score.desc(), ExceptionCase.created_at.asc())
    )
    if batch_id:
        stmt = stmt.where(ExceptionCase.batch_id == batch_id)
    if priority:
        stmt = stmt.where(ExceptionCase.priority == priority)
    if issue_type:
        stmt = stmt.where(ExceptionCase.issue_type == issue_type)
    if assignee == "unassigned":
        stmt = stmt.where(ExceptionCase.assigned_to.is_(None))
    elif assignee:
        stmt = stmt.where(ExceptionCase.assigned_to == assignee)
    if status:
        stmt = stmt.where(ExceptionCase.status == status)
    rows = list(db.scalars(stmt).unique())
    if search:
        needle = search.lower().strip()
        rows = [
            row
            for row in rows
            if needle in row.record.employee_id.lower()
            or needle in row.record.employee_name.lower()
            or needle in row.issue_label.lower()
            or needle in row.record.team.lower()
        ]
    return rows


def resolve_exception(
    db: Session,
    *,
    exception_id: str,
    outcome: ResolutionOutcome,
    reason_code: ReasonCode,
    note: str | None,
    resolved_by: str,
    resolved_at: datetime | None = None,
    handling_minutes: float | None = None,
) -> ExceptionCase:
    case = get_exception(db, exception_id)
    if case is None:
        raise ReviewError("Eccezione non trovata")
    if case.resolution is not None:
        raise ReviewError("L'eccezione ha già una risoluzione")
    if not resolved_by.strip():
        raise ReviewError("resolved_by è obbligatorio")

    now = resolved_at or datetime.utcnow()
    minutes = handling_minutes
    if minutes is None:
        minutes = max(1.0, round((now - case.created_at).total_seconds() / 60, 1))

    case.status = OUTCOME_STATUS[outcome].value
    resolution = ReviewResolution(
        id=new_id("res"),
        exception_id=case.id,
        outcome=outcome.value,
        reason_code=reason_code.value,
        note=note,
        resolved_by=resolved_by,
        resolved_at=now,
        handling_minutes=minutes,
    )
    db.add(resolution)
    case.resolution = resolution
    db.add(
        AuditEvent(
            id=new_id("aud"),
            entity_type="exception",
            entity_id=case.id,
            event_type="exception_resolved",
            payload_json=json.dumps(
                {
                    "outcome": outcome.value,
                    "reason_code": reason_code.value,
                    "status": case.status,
                }
            ),
            actor=resolved_by,
            created_at=now,
        )
    )
    db.flush()
    db.refresh(case)
    return case
