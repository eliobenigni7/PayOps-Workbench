from app.domain.enums import Priority, Routing
from app.rules.engine import evaluate_record
from app.scoring.scorer import score_record
from tests.test_rules import make_record


def test_clean_record_is_auto_cleared():
    record = make_record()
    decision = score_record(record, evaluate_record(record))
    assert decision.routing == Routing.AUTO_CLEARED
    assert decision.risk_score == 0
    assert decision.breakdown == []


def test_hero_salary_anomaly_is_critical_and_explained():
    record = make_record(
        employee_id="EMP-1042",
        employee_name="Sara Romano",
        gross_salary=6140,
        previous_gross_salary=4320,
        avg_6m_gross=4320,
        salary_change_event=False,
    )
    decision = score_record(record, evaluate_record(record))
    assert decision.routing == Routing.NEEDS_REVIEW
    assert decision.priority == Priority.CRITICAL
    assert decision.risk_score >= 90
    components = {item.component: item.value for item in decision.breakdown}
    assert set(components) == {"severity", "financial_exposure", "rule_confidence", "missing_support_event"}
    assert components["missing_support_event"] == 15
    assert sum(components.values()) == decision.risk_score
    assert {item.rule_id for item in decision.triggered_rules} >= {
        "SALARY_VARIATION",
        "MISSING_SALARY_EVENT",
        "OUTSIDE_HISTORICAL_RANGE",
    }


def test_same_input_same_score():
    record = make_record(iban_present=False, overtime_hours=28)
    first = score_record(record, evaluate_record(record))
    second = score_record(record, evaluate_record(record))
    assert first.model_dump() == second.model_dump()


def test_missing_iban_is_high_not_auto_cleared():
    record = make_record(iban_present=False)
    decision = score_record(record, evaluate_record(record))
    assert decision.routing == Routing.NEEDS_REVIEW
    assert decision.issue_type.value == "missing_bank_information"
    assert decision.priority in {Priority.HIGH, Priority.MEDIUM, Priority.CRITICAL}
