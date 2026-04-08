"""Download abstraction for public verification data."""

from __future__ import annotations

from services.audit_service.payload_sanitizer import sanitize_audit_payload


def fetch_public_data(
    result_hash: str,
    audit_digest: str,
    metadata: dict[str, object] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {"result_hash": result_hash, "audit_digest": audit_digest}
    if metadata:
        payload["metadata"] = sanitize_audit_payload(metadata)
    return payload
