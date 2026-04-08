"""Offline sync failure injection helpers."""

from __future__ import annotations

from services.audit_service.payload_sanitizer import sanitize_audit_payload


def inject_sync_failure(queue_depth: int, diagnostics: dict[str, object] | None = None) -> dict[str, object]:
    result = {"scenario": "sync_failure", "queue_depth": queue_depth, "recovery_required": queue_depth > 0}
    if diagnostics:
        result["diagnostics"] = sanitize_audit_payload(diagnostics)
    return result
