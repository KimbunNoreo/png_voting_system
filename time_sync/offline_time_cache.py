"""Cached trusted time for disconnected operation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class OfflineTimeCache:
    cached_at: datetime | None = None
    trusted_time: datetime | None = None
    ttl_seconds: int = 3600

    def store(self, trusted_time: datetime, cached_at: datetime) -> None:
        self.trusted_time = trusted_time
        self.cached_at = cached_at

    def get(self, now: datetime) -> datetime:
        if self.trusted_time is None or self.cached_at is None:
            raise ValueError("No trusted time cached")
        if now - self.cached_at > timedelta(seconds=self.ttl_seconds):
            raise ValueError("Cached trusted time has expired")
        return self.trusted_time
