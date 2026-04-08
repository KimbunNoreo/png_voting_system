from __future__ import annotations
from datetime import datetime, timedelta, timezone
class TimeSyncValidator:
    def __init__(self, max_drift_seconds: int = 120) -> None:
        self.max_drift = timedelta(seconds=max_drift_seconds)
    def validate(self, device_time: datetime, trusted_time: datetime | None = None) -> None:
        trusted = trusted_time or datetime.now(timezone.utc)
        if abs(trusted - device_time) > self.max_drift:
            raise ValueError("Device time drift exceeds allowed threshold")