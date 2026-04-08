"""Cut-off enforcement for election closing times."""

from __future__ import annotations

from datetime import datetime


def assert_before_cutoff(now: datetime, cutoff: datetime) -> None:
    if now > cutoff:
        raise ValueError("Election cut-off has passed")
