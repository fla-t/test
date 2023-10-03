from datetime import datetime, timezone


def now_in_utc() -> datetime:
    """Current time in UTC time zone"""

    return datetime.now(timezone.utc)
