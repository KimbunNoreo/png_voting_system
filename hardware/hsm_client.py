"""Hardware security module client abstraction."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class HSMClient:
    keys: dict[str, str] = field(default_factory=dict)

    def import_key(self, key_id: str, pem: str) -> None:
        self.keys[key_id] = pem

    def export_key(self, key_id: str) -> str:
        return self.keys[key_id]
