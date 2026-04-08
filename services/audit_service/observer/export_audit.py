"""Export audit logs for third-party review."""

from __future__ import annotations

import json

from services.audit_service.logger.worm_logger import WORMLogger
from services.audit_service.observer.observer_auth import require_observer_token


def export_audit_log(observer_token: str, logger: WORMLogger) -> str:
    require_observer_token(observer_token)
    payload = [
        {
            "timestamp": entry.timestamp,
            "event_type": entry.event_type,
            "payload": entry.payload,
            "previous_hash": entry.previous_hash,
            "entry_hash": entry.entry_hash,
        }
        for entry in logger.entries()
    ]
    return json.dumps(payload, sort_keys=True)
