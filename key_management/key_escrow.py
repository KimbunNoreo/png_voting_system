"""Key escrow registry."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class KeyEscrow:
    escrowed: dict[str, list[str]] = field(default_factory=dict)

    def escrow(self, key_id: str, shares: list[str]) -> None:
        self.escrowed[key_id] = list(shares)

    def retrieve(self, key_id: str) -> list[str]:
        return list(self.escrowed[key_id])
