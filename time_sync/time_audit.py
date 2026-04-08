"""Audit records for time synchronization events."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimeAuditRecord:
    device_id: str
    timestamp_iso: str
    trusted_source: str
    drift_seconds: int
    accepted: bool


def record_time_sync(
    device_id: str,
    timestamp_iso: str,
    trusted_source: str,
    drift_seconds: int,
    accepted: bool,
) -> TimeAuditRecord:
    return TimeAuditRecord(
        device_id=device_id,
        timestamp_iso=timestamp_iso,
        trusted_source=trusted_source,
        drift_seconds=drift_seconds,
        accepted=accepted,
    )
