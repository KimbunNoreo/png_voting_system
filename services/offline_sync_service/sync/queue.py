"""Persistent queue abstraction for offline sync operations."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from services.audit_service.payload_sanitizer import sanitize_audit_payload


@dataclass
class SyncQueue:
    _items: deque[dict[str, object]] = field(default_factory=deque)

    def push(self, item: dict[str, object]) -> None:
        self._items.append(sanitize_audit_payload(item))

    def pop(self) -> dict[str, object]:
        if not self._items:
            raise IndexError("Sync queue is empty")
        return self._items.popleft()

    def peek_all(self) -> list[dict[str, object]]:
        return list(self._items)

    def __len__(self) -> int:
        return len(self._items)
