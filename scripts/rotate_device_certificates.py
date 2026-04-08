"""Device certificate rotation planning helper."""

from __future__ import annotations


def plan_rotation(device_ids: list[str]) -> list[dict[str, str]]:
    return [{"device_id": device_id, "action": "rotate_certificate"} for device_id in device_ids]
