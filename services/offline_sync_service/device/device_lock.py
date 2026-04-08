"""Device lock state for tamper responses."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DeviceLock:
    locked: bool = False
    reason: str = ""

    def activate(self, reason: str) -> None:
        self.locked = True
        self.reason = reason
