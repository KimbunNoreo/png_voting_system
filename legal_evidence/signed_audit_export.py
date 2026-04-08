"""Signed audit export creation."""

from __future__ import annotations

import json

from services.audit_service.payload_sanitizer import sanitize_audit_payload
from services.voting_service.crypto.crypto_provider import Phase1CryptoProvider


def create_signed_audit_export(payload: str, signing_key_pem: str) -> dict[str, str]:
    try:
        parsed_payload = json.loads(payload)
    except json.JSONDecodeError:
        sanitized_payload = payload
    else:
        if isinstance(parsed_payload, dict):
            sanitized_payload = json.dumps(sanitize_audit_payload(parsed_payload), sort_keys=True)
        elif isinstance(parsed_payload, list):
            sanitized_payload = json.dumps(
                [sanitize_audit_payload(item) if isinstance(item, dict) else item for item in parsed_payload],
                sort_keys=True,
            )
        else:
            sanitized_payload = payload
    crypto = Phase1CryptoProvider()
    signature = crypto.sign_bytes(sanitized_payload.encode("utf-8"), signing_key_pem)
    return {"payload": sanitized_payload, "signature": signature}
