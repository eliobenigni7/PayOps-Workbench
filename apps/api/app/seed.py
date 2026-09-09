from __future__ import annotations

import random
from copy import deepcopy
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.db.models import Batch, ReviewResolution
from app.domain.enums import ExceptionStatus, IssueType, ReasonCode, ResolutionOutcome
from app.services.batch_service import process_batch
from app.services.catalog import OPERATORS, PLAYBOOKS
from app.services.improvement_service import refresh_opportunities
from app.util import new_id

FIRST = [
    "Giulia", "Luca", "Sara", "Marco", "Elena", "Andrea", "Chiara", "Matteo", "Francesca", "Davide",
    "Alessia", "Stefano", "Sofia", "Paolo", "Greta", "Nicola", "Valentina", "Riccardo", "Martina", "Federico",
    "Ilaria", "Giorgio", "Elisa", "Alberto", "Silvia", "Lorenzo", "Beatrice", "Simone", "Anna", "Pietro",
]
LAST = [
    "Ferri", "Conti", "Romano", "Villa", "Moretti", "Greco", "Riva", "Sala", "Gallo", "Bruno",
    "Marchetti", "Caruso", "Bianchi", "Ricci", "De Luca", "Fontana", "Costa", "Lombardi", "Esposito", "Ferrari",
    "Colombo", "Martini", "Gentile", "Barone", "Leone", "Mancini", "Santoro", "Farina", "Coppola", "Serra",
]
TEAMS = [
    "Sales", "Operations", "Engineering", "Marketing", "Finance", "People",
    "Customer Success", "Legal", "Product", "Support",
]
BASE_SALARIES = [2800, 2940, 3040, 3100, 3210, 3380, 3520, 3680, 3860, 4100, 4320, 4480, 4650, 4920, 5100]

HERO_NAMES = {
    1001: ("Giulia Ferri", "Sales"),
    1002: ("Luca Conti", "Operations"),
    1004: ("Marco Villa", "Marketing"),
    1005: ("Elena Moretti", "Finance"),
    1006: ("Andrea Greco", "Sales"),
    1007: ("Chiara Riva", "People"),
    1008: ("Matteo Sala", "Engineering"),
    1009: ("Francesca Gallo", "Operations"),
    1010: ("Davide Bruno", "Customer Success"),
    1011: ("Alessia Marchetti", "Operations"),
    1012: ("Stefano Caruso", "Engineering"),
    1042: ("Sara Romano", "Engineering"),
}


def _name_for(emp_no: int, rng: random.Random) -> tuple[str, str]:
    if emp_no in HERO_NAMES:
        return HERO_NAMES[emp_no]
    first = FIRST[(emp_no + rng.randrange(0, 30)) % len(FIRST)]
    last = LAST[(emp_no * 3 + rng.randrange(0, 30)) % len(LAST)]
    team = TEAMS[emp_no % len(TEAMS)]
    return f"{first} {last}", team


def _clean_row(emp_no: int, period: str, rng: random.Random) -> dict:
    name, team = _name_for(emp_no, rng)
    previous = rng.choice(BASE_SALARIES)
    drift = rng.choice([-40, -20, -10, 0, 0, 0, 10, 20, 30, 50])
    gross = previous + drift
    return {
        "employee_id": f"EMP-{emp_no}",
        "employee_name": name,
        "team": team,
        "period": period,
        "gross_salary": gross,
        "previous_gross_salary": previous,
        "avg_6m_gross": round(previous * rng.uniform(0.98, 1.02), 2),
        "regular_hours": 168,
        "overtime_hours": rng.choice([0, 1, 2, 3, 4, 5, 6]),
        "bonus_amount": rng.choice([0, 0, 0, 0, 80, 120]),
        "iban_present": True,
        "salary_change_event": abs(drift) >= 10 and rng.random() < 0.35,
        "manual_override": False,
        "assigned_to": rng.choice([*OPERATORS, None, None]),
    }


def _apply(row: dict, **updates: object) -> dict:
    row.update(updates)
    return row


def build_september_rows(processed_at: datetime) -> list[dict]:
    rng = random.Random(42)
    start_id, count = 1001, 1282
    rows = [_clean_row(emp_no, "2026-09", rng) for emp_no in range(start_id, start_id + count)]
    by_id = {row["employee_id"]: row for row in rows}

    def pick(emp_no: int) -> dict:
        return by_id[f"EMP-{emp_no}"]

    # Hero salary anomaly — EMP-1042 Sara Romano
    _apply(
        pick(1042),
        gross_salary=6140,
        previous_gross_salary=4320,
        avg_6m_gross=4320,
        overtime_hours=3,
        bonus_amount=0,
        iban_present=True,
        salary_change_event=False,
        assigned_to="Sofia Bianchi",
        exception_id="exc_1042",
        created_at=processed_at - timedelta(hours=2, minutes=18),
    )

    missing_iban_ids = [1004, 1011, *range(1100, 1127)]  # 29
    salary_ids = [1130 + i for i in range(17)]  # 17 + hero = 18
    bonus_ids = [1006, 1012, *range(1150, 1164)]  # 16
    overtime_ids = [1005, *range(1170, 1182)]  # 13
    override_ids = [1009, *range(1190, 1199)]  # 10
    missing_event_ids = list(range(1210, 1213))  # 3
    duplicate_ids = [1200, 1201]

    used = {1042, *missing_iban_ids, *salary_ids, *bonus_ids, *overtime_ids, *override_ids, *missing_event_ids, *duplicate_ids}
    assert len(used) == 29 + 18 + 16 + 13 + 10 + 3 + 2  # 91 unique + 2 dup copies later = 93 exception records

    for emp_no in missing_iban_ids:
        _apply(pick(emp_no), iban_present=False, assigned_to=rng.choice([*OPERATORS, None]))

    critical_salary = salary_ids[:7]
    high_salary = salary_ids[7:]
    for emp_no in critical_salary:
        prev = pick(emp_no)["previous_gross_salary"]
        _apply(
            pick(emp_no),
            gross_salary=round(prev * rng.uniform(1.41, 1.52), 2),
            avg_6m_gross=prev,
            salary_change_event=False,
        )
    for emp_no in high_salary:
        prev = pick(emp_no)["previous_gross_salary"]
        _apply(
            pick(emp_no),
            gross_salary=round(prev * rng.uniform(1.31, 1.38), 2),
            avg_6m_gross=prev,
            salary_change_event=False,
        )

    for index, emp_no in enumerate(bonus_ids):
        amount = 2400 if emp_no == 1006 else 1200 if emp_no == 1012 else rng.choice([1600, 1800, 2100, 2500])
        _apply(pick(emp_no), bonus_amount=amount, manual_override=(emp_no == 1012))

    for emp_no in overtime_ids:
        hours = 28 if emp_no == 1005 else rng.choice([22, 24, 26, 30, 41, 42])
        _apply(pick(emp_no), overtime_hours=hours)

    for emp_no in override_ids:
        _apply(pick(emp_no), manual_override=True, bonus_amount=max(pick(emp_no)["bonus_amount"], 0))

    for emp_no in missing_event_ids:
        prev = pick(emp_no)["previous_gross_salary"]
        _apply(
            pick(emp_no),
            gross_salary=round(prev * rng.uniform(1.12, 1.22), 2),
            avg_6m_gross=prev,
            salary_change_event=False,
        )

    created_base = processed_at - timedelta(hours=18)
    open_ids = [row["employee_id"] for row in rows if row["employee_id"] in {f"EMP-{n}" for n in used}]
    for offset, emp_id in enumerate(open_ids):
        row = by_id[emp_id]
        row.setdefault("created_at", created_base + timedelta(minutes=offset * 11))

    duplicates: list[dict] = []
    for emp_no in duplicate_ids:
        original = pick(emp_no)
        original["is_seed_duplicate"] = True
        copy = deepcopy(original)
        copy["record_id"] = new_id("rec")
        copy["exception_id"] = f"exc_{emp_no}b"
        copy["gross_salary"] = original["gross_salary"] + 40
        original["exception_id"] = f"exc_{emp_no}a"
        duplicates.append(copy)

    return rows + duplicates


def build_historical_rows(period: str, seed: int, size: int = 420) -> list[dict]:
    rng = random.Random(seed)
    start_id = 3000 if period.endswith("08") else 4000
    rows = [_clean_row(start_id + index, period, rng) for index in range(size)]

    def take(count: int, start: int) -> list[dict]:
        return rows[start : start + count]

    for row in take(22 if period.endswith("08") else 18, 10):
        row["iban_present"] = False
    for row in take(16 if period.endswith("08") else 14, 40):
        row["gross_salary"] = round(row["previous_gross_salary"] * rng.uniform(1.32, 1.48), 2)
        row["avg_6m_gross"] = row["previous_gross_salary"]
        row["salary_change_event"] = False
    for row in take(14, 70):
        row["bonus_amount"] = rng.choice([1600, 1900, 2200])
    for row in take(12, 90):
        row["overtime_hours"] = rng.choice([23, 27, 33])
    for row in take(10, 110):
        row["manual_override"] = True
    for row in take(6, 130):
        row["gross_salary"] = round(row["previous_gross_salary"] * rng.uniform(1.11, 1.18), 2)
        row["salary_change_event"] = False
        row["avg_6m_gross"] = row["previous_gross_salary"]
    original = rows[150]
    duplicate = deepcopy(original)
    duplicate["record_id"] = new_id("rec")
    rows.append(duplicate)
    return rows


RESOLUTION_POLICY = {
    IssueType.MISSING_BANK_INFORMATION: (ResolutionOutcome.CONFIRM_ISSUE, ReasonCode.ONBOARDING_INCOMPLETE, 0.82),
    IssueType.SALARY_DISCREPANCY: (ResolutionOutcome.MARK_EXPECTED, ReasonCode.SALARY_INCREASE, 0.58),
    IssueType.MISSING_HR_EVENT: (ResolutionOutcome.CONFIRM_ISSUE, ReasonCode.MISSING_SOURCE_DATA, 0.7),
    IssueType.BONUS_ANOMALY: (ResolutionOutcome.MARK_EXPECTED, ReasonCode.ONE_OFF_BONUS, 0.62),
    IssueType.OVERTIME_ISSUE: (ResolutionOutcome.CONFIRM_ISSUE, ReasonCode.DATA_CORRECTION, 0.55),
    IssueType.MANUAL_OVERRIDE: (ResolutionOutcome.MARK_EXPECTED, ReasonCode.MANUAL_ADJUSTMENT, 0.7),
    IssueType.DUPLICATE_RECORD: (ResolutionOutcome.CONFIRM_ISSUE, ReasonCode.DUPLICATE_PAYMENT, 0.9),
}


def _resolve_historical(db: Session, batch: Batch, rng: random.Random, resolved_at: datetime) -> None:
    from sqlalchemy import select
    from app.db.models import ExceptionCase

    cases = list(db.scalars(select(ExceptionCase).where(ExceptionCase.batch_id == batch.id)))
    for case in cases:
        issue = IssueType(case.issue_type)
        default_outcome, default_reason, confirm_rate = RESOLUTION_POLICY[issue]
        if rng.random() < confirm_rate:
            outcome, reason = ResolutionOutcome.CONFIRM_ISSUE, (
                ReasonCode.PROCESS_GAP if issue == IssueType.MISSING_BANK_INFORMATION else default_reason
            )
            if issue == IssueType.MISSING_BANK_INFORMATION:
                reason = ReasonCode.ONBOARDING_INCOMPLETE
        else:
            outcome, reason = ResolutionOutcome.MARK_EXPECTED, default_reason
            if rng.random() < 0.08:
                outcome, reason = ResolutionOutcome.ESCALATE, ReasonCode.OTHER
        playbook = PLAYBOOKS[issue]
        minutes = max(2.5, round(rng.gauss(playbook.default_handling_minutes, 1.1), 1))
        case.status = (
            ExceptionStatus.ESCALATED.value
            if outcome == ResolutionOutcome.ESCALATE
            else ExceptionStatus.RESOLVED.value
        )
        if outcome == ResolutionOutcome.ESCALATE:
            case.status = ExceptionStatus.RESOLVED.value
            outcome = ResolutionOutcome.ESCALATE
        resolution = ReviewResolution(
            id=new_id("res"),
            exception_id=case.id,
            outcome=outcome.value,
            reason_code=reason.value,
            note="Seeded historical resolution for the demo insights window.",
            resolved_by=rng.choice(OPERATORS),
            resolved_at=resolved_at - timedelta(minutes=rng.randrange(30, 4000)),
            handling_minutes=minutes,
        )
        db.add(resolution)
        case.resolution = resolution


def seed_if_empty(db: Session) -> None:
    existing = db.query(Batch).first()
    if existing is not None:
        return
    seed_demo(db)


def seed_demo(db: Session) -> None:
    september_at = datetime(2026, 9, 9, 9, 42, 0)
    august_at = datetime(2026, 8, 10, 10, 5, 0)
    july_at = datetime(2026, 7, 9, 9, 18, 0)

    july = process_batch(
        db,
        build_historical_rows("2026-07", seed=7),
        period="2026-07",
        source="seed:historical",
        batch_id="bat_2026_07",
        processed_at=july_at,
        created_at=july_at - timedelta(hours=2),
    )
    _resolve_historical(db, july, random.Random(7), july_at + timedelta(days=4))

    august = process_batch(
        db,
        build_historical_rows("2026-08", seed=8),
        period="2026-08",
        source="seed:historical",
        batch_id="bat_2026_08",
        processed_at=august_at,
        created_at=august_at - timedelta(hours=2),
    )
    _resolve_historical(db, august, random.Random(8), august_at + timedelta(days=5))

    process_batch(
        db,
        build_september_rows(september_at),
        period="2026-09",
        source="seed:demo",
        batch_id="bat_2026_09",
        processed_at=september_at,
        created_at=september_at - timedelta(hours=3),
    )
    refresh_opportunities(db)
    db.flush()
