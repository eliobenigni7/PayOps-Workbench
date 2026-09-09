from datetime import datetime

from app.ai.providers import MockProvider
from app.rules.engine import evaluate_record
from app.services.ai_service import AIService
from app.services.batch_service import process_batch
from app.services.review_service import get_exception
from tests.test_rules import make_record


def test_mock_provider_does_not_invent_or_approve():
    record = make_record(
        employee_id="EMP-1042",
        gross_salary=6140,
        previous_gross_salary=4320,
        avg_6m_gross=4320,
    )
    triggered = [item for item in evaluate_record(record) if item.triggered]
    draft = MockProvider().investigate(record, triggered, "Salary anomaly", 96)
    blob = " ".join([draft["summary"], *draft["evidence"], *draft["suggested_checks"]]).lower()
    assert "should be approved" not in blob
    assert "payment approved" not in blob
    assert "legal entitlement" not in blob
    assert "6,140" in draft["summary"] or "6140" in draft["summary"].replace(",", "")
    assert "no corresponding salary-change event" in draft["summary"].lower()
    assert any("does not approve" in item.lower() for item in draft["limitations"])


def test_investigate_does_not_change_exception_status(db):
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
            }
        ],
        period="2026-09",
        source="test",
        processed_at=datetime(2026, 9, 9, 9, 42, 0),
    )
    case = get_exception(db, "exc_1042")
    assert case is not None
    status_before = case.status
    AIService("mock").investigate(db, case)
    db.refresh(case)
    assert case.status == status_before == "open"
    assert case.resolution is None
    assert len(case.investigations) == 1
