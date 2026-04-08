"""Operational NID connectivity test helper."""

from __future__ import annotations

from config import get_settings


def run() -> dict[str, object]:
    settings = get_settings()
    return {"base_url": settings.nid_integration.base_url, "mtls_required": True}
