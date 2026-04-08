"""Simulated HSM integration for key lifecycle operations."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SimulatedHSM:
    keys: dict[str, str] = field(default_factory=dict)

    def store_key(self, key_id: str, pem: str) -> None:
        self.keys[key_id] = pem

    def fetch_key(self, key_id: str) -> str:
        return self.keys[key_id]
