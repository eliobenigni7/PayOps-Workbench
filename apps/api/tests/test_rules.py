from app.domain.types import NormalizedRecord
from app.rules.engine import evaluate_record
from app.rules.rules import RULES_BY_ID


def make_record(**overrides) -> NormalizedRecord:
    payload = dict(
        employee_id="EMP-1000",
        employee_name="Test User",
        team="Engineering",
        period="2026-09",
        gross_salary=4000,
        previous_gross_salary=4000,
        avg_6m_gross=4000,
        regular_hours=168,
        overtime_hours=2,
        bonus_amount=0,
        iban_present=True,
        salary_change_event=False,
        manual_override=False,
    )
    payload.update(overrides)
    return NormalizedRecord(**payload)


def triggered_ids(record: NormalizedRecord) -> set[str]:
    return {item.rule_id for item in evaluate_record(record) if item.triggered}


def test_clean_record_triggers_nothing():
    assert triggered_ids(make_record()) == set()


def test_missing_iban():
    assert "MISSING_IBAN" in triggered_ids(make_record(iban_present=False))


def test_salary_variation_threshold():
    assert "SALARY_VARIATION" not in triggered_ids(make_record(gross_salary=5199, previous_gross_salary=4000))
    assert "SALARY_VARIATION" in triggered_ids(make_record(gross_salary=5200, previous_gross_salary=4000))


def test_missing_salary_event():
    ids = triggered_ids(make_record(gross_salary=4600, previous_gross_salary=4000, salary_change_event=False))
    assert "MISSING_SALARY_EVENT" in ids
    ids = triggered_ids(make_record(gross_salary=4600, previous_gross_salary=4000, salary_change_event=True))
    assert "MISSING_SALARY_EVENT" not in ids


def test_implausible_overtime():
    assert "IMPLAUSIBLE_OVERTIME" not in triggered_ids(make_record(overtime_hours=20))
    result = RULES_BY_ID["IMPLAUSIBLE_OVERTIME"](make_record(overtime_hours=41))
    assert result.triggered
    assert result.severity.value == "critical"


def test_unusual_bonus_and_override_and_duplicate():
    assert "UNUSUAL_BONUS" in triggered_ids(make_record(bonus_amount=1800))
    assert "MANUAL_OVERRIDE" in triggered_ids(make_record(manual_override=True))
    assert "DUPLICATE_RECORD" in triggered_ids(make_record(is_duplicate=True, duplicate_count=2))


def test_rules_are_deterministic():
    record = make_record(gross_salary=6140, previous_gross_salary=4320, avg_6m_gross=4320)
    first = [item.model_dump() for item in evaluate_record(record)]
    second = [item.model_dump() for item in evaluate_record(record)]
    assert first == second
