"""NID outage simulation helpers."""

from __future__ import annotations


def simulate_nid_outage(duration_seconds: int) -> dict[str, object]:
    if duration_seconds < 0:
        raise ValueError("Outage duration must be non-negative")
    return {"scenario": "nid_outage", "duration_seconds": duration_seconds, "fallback_required": True}
