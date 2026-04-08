"""Tamper detection for audit chains."""

from __future__ import annotations

import hashlib
import json

from services.audit_service.logger.worm_logger import AuditEntry


def verify_hash_chain(entries: list[AuditEntry]) -> bool:
    previous_hash = "GENESIS"
    for entry in entries:
        canonical = json.dumps(
            {
                "timestamp": entry.timestamp,
                "event_type": entry.event_type,
                "payload": entry.payload,
                "previous_hash": previous_hash,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        if entry.entry_hash != expected or entry.previous_hash != previous_hash:
            return False
        previous_hash = entry.entry_hash
    return True
