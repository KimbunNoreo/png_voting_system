"""NID outage simulation helpers."""

from __future__ import annotations


def simulate_nid_outage(duration_seconds: int) -> dict[str, object]:
    return {"scenario": "nid_outage", "duration_seconds": duration_seconds, "fallback_required": True}
