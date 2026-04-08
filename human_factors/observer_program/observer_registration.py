"""Observer registration helpers."""

from __future__ import annotations


def register_observer(observer_id: str, organization: str) -> dict[str, str]:
    return {"observer_id": observer_id, "organization": organization}
