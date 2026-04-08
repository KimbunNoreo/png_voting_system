"""Network partition simulation helpers."""

from __future__ import annotations


def simulate_network_partition(connected: bool) -> dict[str, object]:
    return {"scenario": "network_partition", "service_connected": connected, "degraded": not connected}
