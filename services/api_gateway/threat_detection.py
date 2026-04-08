"""Deterministic threat detection rules for gateway traffic."""

from __future__ import annotations

import re


class ThreatDetector:
    """Flags obviously malicious request patterns without AI inference."""

    _blocked_patterns = (
        re.compile(r"(?i)(union\s+select|drop\s+table|insert\s+into|or\s+1=1)"),
        re.compile(r"(?i)(<script|javascript:|onerror\s*=|onload\s*=)"),
        re.compile(r"(?i)(\.\./|\.\.\\|/etc/passwd|boot\.ini|cmd\.exe|powershell\.exe)"),
        re.compile(r"(?i)(;\s*(shutdown|rm|del|curl|wget)\b)"),
    )

    def inspect(self, request: dict[str, object]) -> None:
        headers = request.get("headers", {})
        if not isinstance(headers, dict):
            headers = {}
        header_payload = " ".join(f"{key}:{value}" for key, value in headers.items())
        query = request.get("query", {})
        query_payload = str(query)
        payload = " ".join(
            [
                str(request.get("path", "")),
                query_payload,
                str(request.get("body", "")),
                header_payload,
            ]
        )
        for pattern in self._blocked_patterns:
            if pattern.search(payload):
                raise ValueError("Threat detection rule triggered")
