from __future__ import annotations

import csv
import io
import json
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import OpportunityStatusRequest, ResolveRequest
from app.config import settings
from app.db.models import AuditEvent, Batch, ExceptionCase
from app.db.session import get_db
from app.domain.enums import (
    ISSUE_LABELS,
    OUTCOME_LABELS,
    REASON_LABELS,
    ImprovementStatus,
    IssueType,
    ReasonCode,
    ResolutionOutcome,
)
from app.services.ai_service import AIService, AIUnavailable
from app.services.batch_service import CSV_FIELDS, process_batch
from app.services.catalog import OPERATORS
from app.services.improvement_service import get_opportunity, list_opportunities, update_opportunity_status
from app.services.insight_service import (
    dashboard_payload,
    insights_payload,
    latest_batch,
    list_batches,
    previous_batch,
)
from app.services.review_service import ReviewError, get_exception, list_exceptions, resolve_exception

router = APIRouter()
ai_service = AIService()


def _age_hours(created_at: datetime, now: datetime | None = None) -> float:
    current = now or datetime.utcnow()
    return round((current - created_at).total_seconds() / 3600, 1)


def _list_item(case: ExceptionCase) -> dict:
    return {
        "id": case.id,
        "employee_id": case.record.employee_id,
        "employee_name": case.record.employee_name,
        "team": case.record.team,
        "issue_label": case.issue_label,
        "issue_type": case.issue_type,
        "priority": case.priority,
        "risk_score": case.risk_score,
        "financial_exposure": case.financial_exposure,
        "age_hours": _age_hours(case.created_at),
        "assigned_to": case.assigned_to,
        "status": case.status,
        "has_ai_investigation": bool(case.investigations),
        "period": case.record.period,
        "batch_id": case.batch_id,
    }


def _context_panel(case: ExceptionCase) -> dict:
    record = case.record
    delta = record.gross_salary - record.previous_gross_salary
    delta_pct = (delta / record.previous_gross_salary * 100) if record.previous_gross_salary else 0
    rows: list[dict] = []
    if case.issue_type in {IssueType.SALARY_DISCREPANCY.value, IssueType.MISSING_HR_EVENT.value}:
        rows = [
            {"label": "Gross salary", "value": record.gross_salary, "format": "eur", "tone": "critical" if abs(delta_pct) >= 40 else "default"},
            {"label": "Previous period", "value": record.previous_gross_salary, "format": "eur"},
            {"label": "6m average", "value": record.avg_6m_gross, "format": "eur"},
            {"label": "Difference", "value": delta_pct, "format": "pct", "tone": "critical" if abs(delta_pct) >= 30 else "default"},
        ]
    elif case.issue_type == IssueType.MISSING_BANK_INFORMATION.value:
        rows = [
            {"label": "IBAN present", "value": "No", "tone": "critical"},
            {"label": "Gross salary at risk", "value": record.gross_salary, "format": "eur"},
            {"label": "Team", "value": record.team},
        ]
    elif case.issue_type == IssueType.OVERTIME_ISSUE.value:
        rows = [
            {"label": "Overtime hours", "value": record.overtime_hours, "tone": "critical"},
            {"label": "Regular hours", "value": record.regular_hours},
            {"label": "Review threshold", "value": 20},
        ]
    elif case.issue_type == IssueType.BONUS_ANOMALY.value:
        rows = [
            {"label": "Bonus amount", "value": record.bonus_amount, "format": "eur", "tone": "high"},
            {"label": "Gross salary", "value": record.gross_salary, "format": "eur"},
            {"label": "Bonus / gross", "value": (record.bonus_amount / record.gross_salary * 100) if record.gross_salary else 0, "format": "pct"},
        ]
    elif case.issue_type == IssueType.DUPLICATE_RECORD.value:
        rows = [
            {"label": "Employee", "value": record.employee_id},
            {"label": "Period", "value": record.period},
            {"label": "Gross salary", "value": record.gross_salary, "format": "eur"},
        ]
    else:
        rows = [
            {"label": "Manual override", "value": "Yes" if record.manual_override else "No"},
            {"label": "Gross salary", "value": record.gross_salary, "format": "eur"},
            {"label": "Bonus", "value": record.bonus_amount, "format": "eur"},
        ]
    return {"title": "What changed", "rows": rows}


def _investigation(item) -> dict:
    return {
        "id": item.id,
        "summary": item.summary,
        "evidence": json.loads(item.evidence_json),
        "suggested_checks": json.loads(item.suggested_checks_json),
        "confidence": item.confidence,
        "limitations": json.loads(item.limitations_json),
        "provider": item.provider,
        "model": item.model,
        "prompt_version": item.prompt_version,
        "created_at": item.created_at.isoformat(),
    }


def _opportunity_payload(item) -> dict:
    return {
        "id": item.id,
        "issue_type": item.issue_type,
        "title": item.title,
        "monthly_occurrences": item.monthly_occurrences,
        "avg_handling_minutes": item.avg_handling_minutes,
        "monthly_effort_hours": item.monthly_effort_hours,
        "false_positive_rate": item.false_positive_rate,
        "trend": item.trend,
        "root_cause_hypothesis": item.root_cause_hypothesis,
        "suggested_intervention": item.suggested_intervention,
        "implementation_effort": item.implementation_effort,
        "expected_impact": item.expected_impact,
        "measurement_kpis": json.loads(item.measurement_kpis_json),
        "expected_effort_removed_hours": item.expected_effort_removed_hours,
        "status": item.status,
        "impact_label": "High impact" if item.expected_effort_removed_hours >= 3 else "Medium impact",
        "effort_label": f"{item.implementation_effort.capitalize()} implementation effort",
    }


@router.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "ai_available": ai_service.available,
        "time": datetime.utcnow().isoformat(),
    }


@router.get("/meta")
def meta() -> dict:
    return {
        "operators": list(OPERATORS),
        "issue_types": [{"value": item.value, "label": ISSUE_LABELS[item]} for item in IssueType],
        "outcomes": [{"value": item.value, "label": OUTCOME_LABELS[item]} for item in ResolutionOutcome],
        "reason_codes": [{"value": item.value, "label": REASON_LABELS[item]} for item in ReasonCode],
        "ai_available": ai_service.available,
        "ai_provider": settings.ai_provider,
    }


@router.get("/batches")
def batches(db: Session = Depends(get_db)) -> dict:
    items = list_batches(db)
    return {
        "items": [
            {
                "id": item.id,
                "period": item.period,
                "source": item.source,
                "status": item.status,
                "record_count": item.record_count,
                "processed_at": item.processed_at.isoformat() if item.processed_at else None,
            }
            for item in items
        ]
    }


@router.get("/batches/{batch_id}/summary")
def batch_summary(batch_id: str, db: Session = Depends(get_db)) -> dict:
    batch = db.get(Batch, batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    payload = dashboard_payload(db, batch)
    payload["ai_available"] = ai_service.available
    return payload


@router.get("/dashboard")
def dashboard(batch_id: str | None = None, db: Session = Depends(get_db)) -> dict:
    batch = db.get(Batch, batch_id) if batch_id else latest_batch(db)
    if batch is None:
        raise HTTPException(status_code=404, detail="No processed batch")
    payload = dashboard_payload(db, batch)
    payload["ai_available"] = ai_service.available
    payload["batches"] = [
        {"id": item.id, "period": item.period, "record_count": item.record_count}
        for item in list_batches(db)
    ]
    payload["previous_batch_id"] = previous_batch(db, batch).id if previous_batch(db, batch) else None
    return payload


@router.post("/batches/import")
async def import_batch(file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    raw = (await file.read()).decode("utf-8")
    reader = csv.DictReader(io.StringIO(raw))
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV is missing a header row")
    missing = [field for field in CSV_FIELDS if field not in reader.fieldnames]
    if missing:
        raise HTTPException(status_code=400, detail=f"CSV is missing fields: {', '.join(missing)}")
    rows = list(reader)
    if not rows:
        raise HTTPException(status_code=400, detail="CSV has no data rows")
    period = rows[0].get("period") or datetime.utcnow().strftime("%Y-%m")
    batch = process_batch(db, rows, period=period, source=file.filename or "upload.csv")
    return {"batch_id": batch.id, "record_count": batch.record_count, "period": batch.period}


@router.get("/exceptions")
def exceptions(
    batch_id: str | None = None,
    priority: str | None = None,
    issue_type: str | None = None,
    assignee: str | None = None,
    status: str | None = Query(default="open"),
    q: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    if status == "open":
        items = list_exceptions(
            db,
            batch_id=batch_id,
            priority=priority,
            issue_type=issue_type,
            assignee=assignee,
            status=None,
            search=q,
        )
        items = [item for item in items if item.status != "resolved"]
    elif status == "all":
        items = list_exceptions(
            db,
            batch_id=batch_id,
            priority=priority,
            issue_type=issue_type,
            assignee=assignee,
            status=None,
            search=q,
        )
    else:
        items = list_exceptions(
            db,
            batch_id=batch_id,
            priority=priority,
            issue_type=issue_type,
            assignee=assignee,
            status=status,
            search=q,
        )
    return {"items": [_list_item(item) for item in items], "count": len(items)}


@router.get("/exceptions/{exception_id}")
def exception_detail(exception_id: str, db: Session = Depends(get_db)) -> dict:
    case = get_exception(db, exception_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Exception not found")
    audits = list(
        db.scalars(
            select(AuditEvent)
            .where(AuditEvent.entity_id == case.id)
            .order_by(AuditEvent.created_at.asc())
        )
    )
    latest_ai = max(case.investigations, key=lambda item: item.created_at, default=None)
    record = case.record
    return {
        **_list_item(case),
        "record": {
            "id": record.id,
            "employee_id": record.employee_id,
            "employee_name": record.employee_name,
            "team": record.team,
            "period": record.period,
            "gross_salary": record.gross_salary,
            "previous_gross_salary": record.previous_gross_salary,
            "avg_6m_gross": record.avg_6m_gross,
            "regular_hours": record.regular_hours,
            "overtime_hours": record.overtime_hours,
            "bonus_amount": record.bonus_amount,
            "iban_present": record.iban_present,
            "salary_change_event": record.salary_change_event,
            "manual_override": record.manual_override,
        },
        "context_panel": _context_panel(case),
        "triggered_rules": [
            {
                "rule_id": item.rule_id,
                "severity": item.severity,
                "message": item.message,
                "issue_type": item.issue_type,
                "evidence": json.loads(item.evidence_json),
            }
            for item in case.rule_results
        ],
        "priority_breakdown": [
            {"component": item.component, "value": item.value, "explanation": item.explanation}
            for item in case.breakdown
        ],
        "hr_events": [
            {
                "type": "salary_change",
                "present": record.salary_change_event,
                "note": (
                    "Compensation change recorded in the HR feed for this period."
                    if record.salary_change_event
                    else "No salary-change event found in the provided HR data."
                ),
            }
        ],
        "resolution": None
        if case.resolution is None
        else {
            "outcome": case.resolution.outcome,
            "outcome_label": OUTCOME_LABELS[ResolutionOutcome(case.resolution.outcome)],
            "reason_code": case.resolution.reason_code,
            "reason_label": REASON_LABELS[ReasonCode(case.resolution.reason_code)],
            "note": case.resolution.note,
            "resolved_by": case.resolution.resolved_by,
            "resolved_at": case.resolution.resolved_at.isoformat(),
            "handling_minutes": case.resolution.handling_minutes,
        },
        "investigation": _investigation(latest_ai) if latest_ai else None,
        "ai_available": ai_service.available,
        "audit": [
            {
                "id": item.id,
                "event_type": item.event_type,
                "actor": item.actor,
                "payload": json.loads(item.payload_json or "{}"),
                "created_at": item.created_at.isoformat(),
            }
            for item in audits
        ],
    }


@router.post("/exceptions/{exception_id}/resolve")
def resolve(exception_id: str, body: ResolveRequest, db: Session = Depends(get_db)) -> dict:
    try:
        case = resolve_exception(
            db,
            exception_id=exception_id,
            outcome=body.outcome,
            reason_code=body.reason_code,
            note=body.note,
            resolved_by=body.resolved_by,
        )
    except ReviewError as exc:
        status = 404 if "not found" in str(exc).lower() else 409
        raise HTTPException(status_code=status, detail=str(exc)) from exc
    return exception_detail(exception_id, db)


@router.post("/exceptions/{exception_id}/investigate")
def investigate(exception_id: str, db: Session = Depends(get_db)) -> dict:
    case = get_exception(db, exception_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Exception not found")
    try:
        investigation = ai_service.investigate(db, case)
    except AIUnavailable as exc:
        return {
            "available": False,
            "reason": str(exc),
            "disclaimer": "AI suggestions are informational only. Final resolution requires operator confirmation.",
        }
    return {
        "available": True,
        "disclaimer": "AI suggestions are informational only. Final resolution requires operator confirmation.",
        "investigation": _investigation(investigation),
    }


@router.get("/insights")
def insights(batch_id: str | None = None, db: Session = Depends(get_db)) -> dict:
    batch = db.get(Batch, batch_id) if batch_id else latest_batch(db)
    payload = insights_payload(db, batch)
    payload["opportunities"] = [_opportunity_payload(item) for item in list_opportunities(db)[:3]]
    payload["ai_available"] = ai_service.available
    return payload


@router.get("/improvements")
def improvements(db: Session = Depends(get_db)) -> dict:
    items = list_opportunities(db)
    return {"items": [_opportunity_payload(item) for item in items]}


@router.get("/improvements/{opportunity_id}")
def improvement_detail(opportunity_id: str, db: Session = Depends(get_db)) -> dict:
    item = get_opportunity(db, opportunity_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return _opportunity_payload(item)


@router.post("/improvements/{opportunity_id}/status")
def improvement_status(opportunity_id: str, body: OpportunityStatusRequest, db: Session = Depends(get_db)) -> dict:
    try:
        item = update_opportunity_status(db, opportunity_id, body.status)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _opportunity_payload(item)
