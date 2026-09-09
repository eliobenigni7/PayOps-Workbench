from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import Batch, ExceptionCase, RuleResult
from app.domain.enums import ISSUE_LABELS, ExceptionStatus, IssueType, ResolutionOutcome
from app.services.catalog import BASELINE_REVIEW_SECONDS, PLAYBOOKS


def latest_batch(db: Session) -> Batch | None:
    return db.scalar(select(Batch).order_by(Batch.processed_at.desc()))


def get_batch(db: Session, batch_id: str) -> Batch | None:
    return db.get(Batch, batch_id)


def list_batches(db: Session) -> list[Batch]:
    return list(db.scalars(select(Batch).order_by(Batch.processed_at.desc())))


def previous_batch(db: Session, batch: Batch) -> Batch | None:
    return db.scalar(
        select(Batch)
        .where(Batch.processed_at < batch.processed_at)
        .order_by(Batch.processed_at.desc())
    )


def batch_counts(db: Session, batch: Batch) -> dict[str, int]:
    exceptions = list(db.scalars(select(ExceptionCase).where(ExceptionCase.batch_id == batch.id)))
    openish = [
        item
        for item in exceptions
        if item.status in {ExceptionStatus.OPEN.value, ExceptionStatus.REQUESTED_INFO.value, ExceptionStatus.ESCALATED.value}
    ]
    return {
        "processed": batch.record_count,
        "needs_review": len(exceptions),
        "open_review": len(openish),
        "auto_cleared": batch.record_count - len(exceptions),
        "critical": sum(1 for item in exceptions if item.priority == "critical" and item.status != ExceptionStatus.RESOLVED.value),
        "critical_all": sum(1 for item in exceptions if item.priority == "critical"),
        "resolved": sum(1 for item in exceptions if item.status == ExceptionStatus.RESOLVED.value),
    }


def effort_avoided_minutes(auto_cleared: int) -> float:
    return round(auto_cleared * BASELINE_REVIEW_SECONDS / 60, 1)


def _issue_stats(cases: list[ExceptionCase]) -> dict[str, dict]:
    grouped: dict[str, list[ExceptionCase]] = defaultdict(list)
    for case in cases:
        grouped[case.issue_type].append(case)

    stats: dict[str, dict] = {}
    for issue_type, items in grouped.items():
        resolved = [item for item in items if item.resolution is not None]
        handling = [item.resolution.handling_minutes for item in resolved if item.resolution]
        playbook = PLAYBOOKS.get(IssueType(issue_type))
        avg = round(sum(handling) / len(handling), 1) if handling else (playbook.default_handling_minutes if playbook else 6.0)
        expected = sum(1 for item in resolved if item.resolution and item.resolution.outcome == ResolutionOutcome.MARK_EXPECTED.value)
        confirmed = sum(1 for item in resolved if item.resolution and item.resolution.outcome == ResolutionOutcome.CONFIRM_ISSUE.value)
        stats[issue_type] = {
            "issue_type": issue_type,
            "label": ISSUE_LABELS.get(IssueType(issue_type), issue_type),
            "occurrences": len(items),
            "open": sum(item.status != ExceptionStatus.RESOLVED.value for item in items),
            "resolved": len(resolved),
            "avg_handling_minutes": avg,
            "monthly_effort_hours": round(len(items) * avg / 60, 1),
            "false_positive_rate": round(expected / len(resolved), 3) if resolved else 0.0,
            "confirmed_rate": round(confirmed / len(resolved), 3) if resolved else 0.0,
        }
    return stats


def _rule_quality(db: Session, cases: list[ExceptionCase]) -> list[dict]:
    ids = [case.id for case in cases]
    if not ids:
        return []
    results = list(db.scalars(select(RuleResult).where(RuleResult.exception_id.in_(ids))))
    by_rule: dict[str, list[tuple[RuleResult, ExceptionCase]]] = defaultdict(list)
    cases_by_id = {case.id: case for case in cases}
    for result in results:
        case = cases_by_id.get(result.exception_id)
        if case:
            by_rule[result.rule_id].append((result, case))

    quality = []
    for rule_id, pairs in sorted(by_rule.items()):
        resolved = [case for _, case in pairs if case.resolution is not None]
        expected = sum(1 for case in resolved if case.resolution and case.resolution.outcome == ResolutionOutcome.MARK_EXPECTED.value)
        confirmed = sum(1 for case in resolved if case.resolution and case.resolution.outcome == ResolutionOutcome.CONFIRM_ISSUE.value)
        handling = [case.resolution.handling_minutes for case in resolved if case.resolution]
        quality.append(
            {
                "rule_id": rule_id,
                "trigger_count": len(pairs),
                "resolved_count": len(resolved),
                "confirmed_issue_rate": round(confirmed / len(resolved), 3) if resolved else None,
                "false_positive_rate": round(expected / len(resolved), 3) if resolved else None,
                "avg_handling_minutes": round(sum(handling) / len(handling), 1) if handling else None,
            }
        )
    return sorted(quality, key=lambda item: (item["false_positive_rate"] is None, -(item["false_positive_rate"] or 0), -item["trigger_count"]))


def insights_payload(db: Session, batch: Batch | None = None) -> dict:
    batches = list_batches(db)
    if batch is None:
        batch = batches[0] if batches else None
    if batch is None:
        return {"empty": True}

    prev = previous_batch(db, batch)
    current_cases = list(
        db.scalars(
            select(ExceptionCase)
            .options(selectinload(ExceptionCase.resolution), selectinload(ExceptionCase.record))
            .where(ExceptionCase.batch_id == batch.id)
        )
    )
    previous_cases = []
    if prev:
        previous_cases = list(
            db.scalars(
                select(ExceptionCase)
                .options(selectinload(ExceptionCase.resolution))
                .where(ExceptionCase.batch_id == prev.id)
            )
        )

    window_cases = current_cases + previous_cases
    current_stats = _issue_stats(current_cases)
    previous_stats = _issue_stats(previous_cases)
    window_stats = _issue_stats(window_cases)

    causes = sorted(current_stats.values(), key=lambda item: item["occurrences"], reverse=True)
    total = sum(item["occurrences"] for item in causes) or 1
    top_causes = [
        {
            **item,
            "share": round(item["occurrences"] / total, 3),
            "previous_occurrences": previous_stats.get(item["issue_type"], {}).get("occurrences", 0),
            "trend": _trend(item["occurrences"], previous_stats.get(item["issue_type"], {}).get("occurrences", 0)),
        }
        for item in causes
    ]

    effort_rows = sorted(window_stats.values(), key=lambda item: item["monthly_effort_hours"], reverse=True)
    for row in effort_rows:
        prev_occ = previous_stats.get(row["issue_type"], {}).get("occurrences", 0)
        cur_occ = current_stats.get(row["issue_type"], {}).get("occurrences", 0)
        row["trend"] = _trend(cur_occ, prev_occ)
        row["current_occurrences"] = cur_occ
        row["previous_occurrences"] = prev_occ

    counts = batch_counts(db, batch)
    prev_counts = batch_counts(db, prev) if prev else None
    resolution_mix = _resolution_mix(current_cases + previous_cases)

    return {
        "batch_id": batch.id,
        "period": batch.period,
        "hero_question": "Where are we spending avoidable manual effort?",
        "processed": counts["processed"],
        "auto_cleared": counts["auto_cleared"],
        "needs_review": counts["needs_review"],
        "top_causes": top_causes,
        "effort_by_issue": effort_rows,
        "rule_quality": _rule_quality(db, window_cases),
        "resolution_mix": resolution_mix,
        "previous_period": prev.period if prev else None,
        "critical_delta": (counts["critical_all"] - (prev_counts["critical_all"] if prev_counts else counts["critical_all"])),
        "methodology": {
            "baseline_review_seconds": BASELINE_REVIEW_SECONDS,
            "note": "Time-saved figures are scenario assumptions from the synthetic demo, not measured payroll outcomes.",
        },
    }


def dashboard_payload(db: Session, batch: Batch) -> dict:
    counts = batch_counts(db, batch)
    prev = previous_batch(db, batch)
    prev_counts = batch_counts(db, prev) if prev else None
    insights = insights_payload(db, batch)
    open_cases = list(
        db.scalars(
            select(ExceptionCase)
            .options(selectinload(ExceptionCase.record), selectinload(ExceptionCase.investigations))
            .where(
                ExceptionCase.batch_id == batch.id,
                ExceptionCase.status != ExceptionStatus.RESOLVED.value,
            )
            .order_by(ExceptionCase.risk_score.desc())
        )
    )
    oldest = sorted(open_cases, key=lambda item: item.created_at)[:4]
    preview = open_cases[:6]
    now = datetime.utcnow()
    minutes = effort_avoided_minutes(counts["auto_cleared"])
    hours, mins = divmod(int(minutes), 60)
    return {
        "batch": {
            "id": batch.id,
            "period": batch.period,
            "source": batch.source,
            "status": batch.status,
            "processed_at": batch.processed_at.isoformat() if batch.processed_at else None,
            "record_count": batch.record_count,
        },
        "processed": counts["processed"],
        "auto_cleared": counts["auto_cleared"],
        "auto_cleared_rate": round(counts["auto_cleared"] / counts["processed"], 4) if counts["processed"] else 0,
        "needs_review": counts["open_review"],
        "review_rate": round(counts["open_review"] / counts["processed"], 4) if counts["processed"] else 0,
        "critical": counts["critical"],
        "critical_delta": counts["critical_all"] - prev_counts["critical_all"] if prev_counts else 0,
        "effort_avoided_minutes": minutes,
        "effort_avoided_label": f"{hours}h {mins:02d}m",
        "baseline_seconds_per_record": BASELINE_REVIEW_SECONDS,
        "queue_preview": [_exception_list_item(item, now) for item in preview],
        "top_causes": insights["top_causes"][:5],
        "oldest_unresolved": [_exception_list_item(item, now) for item in oldest],
        "open_count": counts["open_review"],
    }


def _exception_list_item(case: ExceptionCase, now: datetime) -> dict:
    age_hours = round((now - case.created_at).total_seconds() / 3600, 1)
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
        "age_hours": age_hours,
        "assigned_to": case.assigned_to,
        "status": case.status,
        "has_ai_investigation": bool(case.investigations),
        "period": case.record.period,
    }


def _trend(current: int, previous: int) -> str:
    if previous <= 0:
        return "stable" if current == 0 else "up"
    change = (current - previous) / previous
    if change >= 0.08:
        return "up"
    if change <= -0.08:
        return "down"
    return "stable"


def _resolution_mix(cases: list[ExceptionCase]) -> dict[str, int]:
    mix: dict[str, int] = defaultdict(int)
    for case in cases:
        if case.resolution:
            mix[case.resolution.outcome] += 1
        elif case.status == ExceptionStatus.OPEN.value:
            mix["open"] += 1
        else:
            mix[case.status] += 1
    return dict(mix)
