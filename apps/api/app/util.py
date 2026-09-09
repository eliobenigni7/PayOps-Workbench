from datetime import datetime
from uuid import uuid4


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def parse_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def parse_float(value: object, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    return float(value)


def isoformat(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat() + "Z"
