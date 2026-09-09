from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ImprovementOpportunity
from app.domain.enums import ImprovementStatus, IssueType
from app.services.catalog import PLAYBOOKS
from app.services.insight_service import insights_payload
from app.util import new_id


def refresh_opportunities(db: Session) -> list[ImprovementOpportunity]:
    payload = insights_payload(db)
    if payload.get("empty"):
        return []

    effort_rows = payload.get("effort_by_issue") or []
    kept: list[ImprovementOpportunity] = []
    for row in effort_rows:
        if row["occurrences"] < 6:
            continue
        try:
            issue = IssueType(row["issue_type"])
        except ValueError:
            continue
        playbook = PLAYBOOKS[issue]
        existing = db.scalar(select(ImprovementOpportunity).where(ImprovementOpportunity.issue_type == issue.value))
        expected_removed = round(row["monthly_effort_hours"] * playbook.prevention_rate, 1)
        if existing is None:
            existing = ImprovementOpportunity(
                id=new_id("imp"),
                issue_type=issue.value,
                title=playbook.title,
                status=ImprovementStatus.DETECTED.value,
                root_cause_hypothesis=playbook.hypothesis,
                suggested_intervention=playbook.intervention,
                implementation_effort=playbook.effort,
                expected_impact=playbook.impact,
                measurement_kpis_json=json.dumps(list(playbook.kpis)),
            )
            db.add(existing)
        existing.monthly_occurrences = row.get("current_occurrences", row["occurrences"])
        existing.avg_handling_minutes = row["avg_handling_minutes"]
        existing.monthly_effort_hours = row["monthly_effort_hours"]
        existing.false_positive_rate = row["false_positive_rate"]
        existing.trend = row.get("trend", "stable")
        existing.expected_effort_removed_hours = expected_removed
        existing.title = playbook.title
        existing.root_cause_hypothesis = playbook.hypothesis
        existing.suggested_intervention = playbook.intervention
        existing.implementation_effort = playbook.effort
        existing.expected_impact = playbook.impact
        existing.measurement_kpis_json = json.dumps(list(playbook.kpis))
        kept.append(existing)

    db.flush()
    kept.sort(key=lambda item: item.expected_effort_removed_hours, reverse=True)
    return kept


def list_opportunities(db: Session) -> list[ImprovementOpportunity]:
    refresh_opportunities(db)
    return list(
        db.scalars(
            select(ImprovementOpportunity).order_by(ImprovementOpportunity.expected_effort_removed_hours.desc())
        )
    )


def get_opportunity(db: Session, opportunity_id: str) -> ImprovementOpportunity | None:
    refresh_opportunities(db)
    return db.get(ImprovementOpportunity, opportunity_id)


def update_opportunity_status(db: Session, opportunity_id: str, status: ImprovementStatus) -> ImprovementOpportunity:
    item = db.get(ImprovementOpportunity, opportunity_id)
    if item is None:
        raise ValueError("Opportunità non trovata")
    item.status = status.value
    db.flush()
    return item
