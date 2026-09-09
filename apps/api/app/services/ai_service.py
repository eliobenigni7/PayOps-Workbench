from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.ai.providers import DisabledProvider, get_provider
from app.config import settings
from app.db.models import AIInvestigation, AuditEvent, ExceptionCase
from app.domain.types import NormalizedRecord, RuleEvaluation
from app.domain.enums import IssueType, Severity
from app.util import new_id

# Structural boundary: this service has no resolve/approve/update methods for exceptions.


class AIUnavailable(Exception):
    pass


class AIService:
    def __init__(self, provider_name: str | None = None):
        self.provider = get_provider(provider_name or settings.ai_provider)

    @property
    def available(self) -> bool:
        return not isinstance(self.provider, DisabledProvider)

    def investigate(self, db: Session, case: ExceptionCase) -> AIInvestigation:
        if not self.available:
            raise AIUnavailable("AI provider is disabled")

        record = NormalizedRecord(
            employee_id=case.record.employee_id,
            employee_name=case.record.employee_name,
            team=case.record.team,
            period=case.record.period,
            gross_salary=case.record.gross_salary,
            previous_gross_salary=case.record.previous_gross_salary,
            avg_6m_gross=case.record.avg_6m_gross,
            regular_hours=case.record.regular_hours,
            overtime_hours=case.record.overtime_hours,
            bonus_amount=case.record.bonus_amount,
            iban_present=case.record.iban_present,
            salary_change_event=case.record.salary_change_event,
            manual_override=case.record.manual_override,
        )
        triggered = [
            RuleEvaluation(
                rule_id=item.rule_id,
                triggered=item.triggered,
                severity=Severity(item.severity),
                message=item.message,
                issue_type=IssueType(item.issue_type),
                evidence=json.loads(item.evidence_json or "{}"),
            )
            for item in case.rule_results
            if item.triggered
        ]
        draft = self.provider.investigate(record, triggered, case.issue_label, case.risk_score)
        now = datetime.utcnow()
        investigation = AIInvestigation(
            id=new_id("ai"),
            exception_id=case.id,
            summary=draft["summary"],
            evidence_json=json.dumps(draft["evidence"]),
            suggested_checks_json=json.dumps(draft["suggested_checks"]),
            confidence=draft["confidence"],
            limitations_json=json.dumps(draft["limitations"]),
            provider=draft["provider"],
            model=draft["model"],
            prompt_version=draft["prompt_version"],
            created_at=now,
        )
        db.add(investigation)
        db.add(
            AuditEvent(
                id=new_id("aud"),
                entity_type="exception",
                entity_id=case.id,
                event_type="ai_investigation_requested",
                payload_json=json.dumps({"provider": draft["provider"], "model": draft["model"]}),
                actor="operator",
                created_at=now,
            )
        )
        db.flush()
        return investigation
