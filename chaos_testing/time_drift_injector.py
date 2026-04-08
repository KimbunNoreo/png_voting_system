"""Clock drift injection helpers."""

from __future__ import annotations

from datetime import datetime, timedelta


def inject_time_drift(base_time: datetime, drift_seconds: int) -> datetime:
    return base_time + timedelta(seconds=drift_seconds)
