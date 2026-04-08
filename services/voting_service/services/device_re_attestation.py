from __future__ import annotations
from datetime import datetime, timedelta, timezone
class DeviceReAttestationService:
    def __init__(self, interval_hours: int = 24) -> None:
        self.interval = timedelta(hours=interval_hours)
    def assert_fresh(self, attested_at: datetime) -> None:
        if datetime.now(timezone.utc) - attested_at > self.interval: raise ValueError("Device attestation is stale")