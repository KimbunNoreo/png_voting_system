"""Clock drift detection for offline devices."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class DriftResult:
    drift_seconds: int
    within_threshold: bool


def detect_drift(device_time: datetime, trusted_time: datetime, threshold_seconds: int = 120) -> DriftResult:
    drift = abs(int((trusted_time - device_time).total_seconds()))
    return DriftResult(drift_seconds=drift, within_threshold=drift <= threshold_seconds)
