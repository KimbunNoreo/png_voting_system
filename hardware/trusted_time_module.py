"""Hardware trusted time module."""

from __future__ import annotations

from datetime import datetime, timezone


def read_trusted_time() -> datetime:
    return datetime.now(timezone.utc)
