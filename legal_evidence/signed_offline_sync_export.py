"""Signed export helpers for offline sync operation history."""

from __future__ import annotations

import json

from services.audit_service.payload_sanitizer import sanitize_audit_payload
from services.voting_service.crypto.crypto_provider import Phase1CryptoProvider


def create_signed_offline_sync_export(
    operations: list[dict[str, object]],
    signing_key_pem: str,
) -> dict[str, str]:
    """Create a canonical signed export for offline sync operation history."""

    sanitized_operations = [
        sanitize_audit_payload(operation) if isinstance(operation, dict) else operation for operation in operations
    ]
    payload = json.dumps(
        {
            "service": "offline_sync_service",
            "phase": "phase1",
            "operations": sanitized_operations,
        },
        sort_keys=True,
    )
    crypto = Phase1CryptoProvider()
    signature = crypto.sign_bytes(payload.encode("utf-8"), signing_key_pem)
    return {"payload": payload, "signature": signature}
