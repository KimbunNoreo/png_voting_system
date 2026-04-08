"""Short-lived cache for NID verification tokens."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone


@dataclass
class TokenCache:
    ttl_seconds: int = 300
    _data: dict[str, tuple[datetime, object]] = field(default_factory=dict)

    def get(self, key: str) -> object | None:
        item = self._data.get(key)
        if item is None:
            return None
        expires_at, value = item
        if expires_at <= datetime.now(timezone.utc):
            self._data.pop(key, None)
            return None
        return value

    def set(self, key: str, value: object) -> None:
        self._data[key] = (datetime.now(timezone.utc) + timedelta(seconds=self.ttl_seconds), value)