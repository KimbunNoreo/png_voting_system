"""Trusted Platform Module integration simulation."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TPMIntegration:
    sealed_keys: dict[str, str] = field(default_factory=dict)

    def seal_key(self, key_id: str, secret: str) -> None:
        self.sealed_keys[key_id] = secret

    def unseal_key(self, key_id: str) -> str:
        return self.sealed_keys[key_id]
