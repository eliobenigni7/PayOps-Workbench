from sqlalchemy import select

from app.db.models import ExceptionCase
from app.seed import seed_demo
from app.services.insight_service import dashboard_payload, latest_batch


def test_seed_demo_matches_the_operating_story(db):
    seed_demo(db)
    batch = latest_batch(db)
    assert batch is not None
    assert batch.period == "2026-09"
    payload = dashboard_payload(db, batch)
    assert payload["processed"] == 1284
    assert payload["needs_review"] == 93
    assert payload["auto_cleared"] == 1191
    assert payload["critical"] >= 12
    hero = db.scalar(select(ExceptionCase).where(ExceptionCase.id == "exc_1042"))
    assert hero is not None
    assert hero.priority == "critical"
    assert hero.issue_type == "salary_discrepancy"
