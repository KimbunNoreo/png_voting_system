"""Read-only observer API for audit access."""

from __future__ import annotations

from services.audit_service.logger.worm_logger import WORMLogger
from services.audit_service.observer.observer_auth import require_observer_token


def fetch_audit_entries(observer_token: str, logger: WORMLogger) -> list[dict[str, object]]:
    require_observer_token(observer_token)
    return [
        {
            "timestamp": entry.timestamp,
            "event_type": entry.event_type,
            "payload": entry.payload,
            "entry_hash": entry.entry_hash,
        }
        for entry in logger.entries()
    ]
