from app.domain.types import NormalizedRecord, RuleEvaluation
from app.rules.rules import RULES, RULES_BY_ID


def evaluate_record(record: NormalizedRecord) -> list[RuleEvaluation]:
    """Run the deterministic rule set. Same input always yields the same evaluations."""
    return [rule(record) for rule in RULES]


def triggered_rules(record: NormalizedRecord) -> list[RuleEvaluation]:
    return [result for result in evaluate_record(record) if result.triggered]


__all__ = ["evaluate_record", "triggered_rules", "RULES", "RULES_BY_ID"]
