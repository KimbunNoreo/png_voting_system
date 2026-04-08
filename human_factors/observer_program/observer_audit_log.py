"""Observer audit log helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ObserverAuditLog:
    observer_id: str
    action: str


def log_observer_action(observer_id: str, action: str) -> ObserverAuditLog:
    return ObserverAuditLog(observer_id, action)
