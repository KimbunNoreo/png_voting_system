"""Redact identity-bearing fields from audit payloads."""

from __future__ import annotations

from typing import Any


REDACTED = "[redacted]"
SENSITIVE_AUDIT_FIELDS = frozenset(
    {
        "name",
        "full_name",
        "first_name",
        "last_name",
        "dob",
        "date_of_birth",
        "address",
        "sub",
        "subject",
        "biometrics",
        "biometric",
        "fingerprint",
        "face_template",
        "iris_template",
        "citizen_reference",
        "national_id",
        "nid_number",
        "phone",
        "email",
        "token",
        "authorization",
    }
)


def sanitize_audit_payload(payload: dict[str, object]) -> dict[str, object]:
    """Recursively redact identity-bearing values from audit payloads."""

    return _sanitize_value(payload)


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized: dict[str, Any] = {}
        for key, item in value.items():
            normalized_key = str(key).strip().lower()
            if normalized_key in SENSITIVE_AUDIT_FIELDS:
                sanitized[str(key)] = REDACTED
            else:
                sanitized[str(key)] = _sanitize_value(item)
        return sanitized
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value]
    if isinstance(value, tuple):
        return [_sanitize_value(item) for item in value]
    return value
