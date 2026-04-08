"""Sealed storage for device secrets."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SealedStorage:
    values: dict[str, str] = field(default_factory=dict)

    def store(self, key: str, value: str) -> None:
        self.values[key] = value

    def load(self, key: str) -> str:
        return self.values[key]
