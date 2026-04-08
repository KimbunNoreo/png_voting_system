from datetime import datetime, timezone
def current_attestation_time() -> datetime:
    return datetime.now(timezone.utc)