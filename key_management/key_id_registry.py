"""Registry of key identifiers and scheme versions."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class KeyIDRegistry:
    keys: dict[str, str] = field(default_factory=dict)

    def register(self, key_id: str, scheme: str) -> None:
        self.keys[key_id] = scheme

    def lookup(self, key_id: str) -> str:
        return self.keys[key_id]
