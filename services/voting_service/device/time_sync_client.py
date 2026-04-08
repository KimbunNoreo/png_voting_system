from datetime import datetime, timezone
def trusted_time_now() -> datetime:
    return datetime.now(timezone.utc)