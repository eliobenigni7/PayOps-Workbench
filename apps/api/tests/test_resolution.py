from datetime import datetime

from app.domain.enums import ReasonCode, ResolutionOutcome
from app.services.ai_service import AIService
from app.services.batch_service import process_batch
from app.services.insight_service import insights_payload
from app.services.review_service import list_exceptions, resolve_exception


def test_ai_service_has_no_mutation_api():
    assert not hasattr(AIService, "resolve")
    assert not hasattr(AIService, "approve")
    assert not hasattr(AIService, "update_exception")
    assert not hasattr(AIService, "clear_exception")


def test_resolve_requires_human_reason_and_updates_insights(db):
    process_batch(
        db,
        [
            {
                "employee_id": "EMP-1042",
                "employee_name": "Sara Romano",
                "team": "Engineering",
                "period": "2026-09",
                "gross_salary": 6140,
                "previous_gross_salary": 4320,
                "avg_6m_gross": 4320,
                "regular_hours": 168,
                "overtime_hours": 3,
                "bonus_amount": 0,
                "iban_present": True,
                "salary_change_event": False,
                "manual_override": False,
                "created_at": datetime(2026, 9, 9, 7, 0, 0),
            },
            {
                "employee_id": "EMP-1002",
                "employee_name": "Luca Conti",
                "team": "Operations",
                "period": "2026-09",
                "gross_salary": 2940,
                "previous_gross_salary": 2940,
                "regular_hours": 168,
                "overtime_hours": 2,
                "bonus_amount": 0,
                "iban_present": True,
                "salary_change_event": False,
                "manual_override": False,
            },
        ],
        period="2026-09",
        source="test",
        batch_id="bat_test",
        processed_at=datetime(2026, 9, 9, 9, 42, 0),
    )

    open_cases = list_exceptions(db, batch_id="bat_test", status="open")
    assert len(open_cases) == 1
    case = open_cases[0]
    assert case.id == "exc_1042"

    before = insights_payload(db)
    assert before["resolution_mix"].get("open") == 1

    resolve_exception(
        db,
        exception_id=case.id,
        outcome=ResolutionOutcome.MARK_EXPECTED,
        reason_code=ReasonCode.SALARY_INCREASE,
        note="Promotion already approved in People Ops.",
        resolved_by="Sofia Bianchi",
        resolved_at=datetime(2026, 9, 9, 10, 0, 0),
        handling_minutes=8.5,
    )

    after = insights_payload(db)
    assert after["resolution_mix"].get("mark_expected") == 1
    assert after["resolution_mix"].get("open", 0) == 0
    salary = next(item for item in after["effort_by_issue"] if item["issue_type"] == "salary_discrepancy")
    assert salary["resolved"] == 1
    assert salary["false_positive_rate"] == 1.0
