"""Read-only observer API key helpers."""

from __future__ import annotations


def issue_read_only_key(observer_id: str) -> str:
    return f"observer-{observer_id}-readonly"
