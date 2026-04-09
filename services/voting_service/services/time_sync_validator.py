from __future__ import annotations

from datetime import datetime, timedelta, timezone


class TimeSyncValidator:
    def __init__(self, max_drift_seconds: int = 120) -> None:
        if not isinstance(max_drift_seconds, int):
            raise ValueError("max_drift_seconds must be an integer")
        if max_drift_seconds <= 0:
            raise ValueError("max_drift_seconds must be positive")
        self.max_drift = timedelta(seconds=max_drift_seconds)

    @staticmethod
    def _require_aware_datetime(value: datetime, field_name: str) -> datetime:
        if not isinstance(value, datetime):
            raise ValueError(f"{field_name} must be a datetime")
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(f"{field_name} must be timezone-aware")
        return value

    def validate(self, device_time: datetime, trusted_time: datetime | None = None) -> None:
        device = self._require_aware_datetime(device_time, "device_time").astimezone(timezone.utc)
        trusted_source = trusted_time or datetime.now(timezone.utc)
        trusted = self._require_aware_datetime(trusted_source, "trusted_time").astimezone(timezone.utc)
        if abs(trusted - device) > self.max_drift:
            raise ValueError("Device time drift exceeds allowed threshold")
