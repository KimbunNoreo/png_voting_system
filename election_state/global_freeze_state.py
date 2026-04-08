"""Global freeze state helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GlobalFreezeState:
    frozen: bool = False
    reason: str = ""

    def activate(self, reason: str) -> None:
        self.frozen = True
        self.reason = reason

    def clear(self) -> None:
        self.frozen = False
        self.reason = ""
