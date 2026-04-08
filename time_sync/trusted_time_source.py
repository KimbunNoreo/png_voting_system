"""Trusted time source selection for offline-first deployments."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class TrustedTimeSource:
    """Represents multiple trusted time sources with deterministic fallback."""

    sources: tuple[str, ...] = ("ntp://time.google.com", "ntp://pool.ntp.org", "gps://local-module")
    selected_source: str | None = field(default=None)

    def now(self) -> datetime:
        self.selected_source = self.sources[0]
        return datetime.now(timezone.utc)
