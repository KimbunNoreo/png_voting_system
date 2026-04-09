"""Device failure simulation helpers."""

from __future__ import annotations

from services.audit_service.payload_sanitizer import sanitize_audit_payload


def simulate_device_failure(device_id: str, failed: bool, diagnostics: dict[str, object] | None = None) -> dict[str, object]:
    normalized_device_id = device_id.strip()
    if not normalized_device_id:
        raise ValueError("Device ID is required")
    result = {"scenario": "device_failure", "device_id": normalized_device_id, "failed": failed}
    if diagnostics:
        result["diagnostics"] = sanitize_audit_payload(diagnostics)
    return result
