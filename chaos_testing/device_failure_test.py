"""Device failure simulation helpers."""

from __future__ import annotations

from services.audit_service.payload_sanitizer import sanitize_audit_payload


def simulate_device_failure(device_id: str, failed: bool, diagnostics: dict[str, object] | None = None) -> dict[str, object]:
    result = {"scenario": "device_failure", "device_id": device_id, "failed": failed}
    if diagnostics:
        result["diagnostics"] = sanitize_audit_payload(diagnostics)
    return result
