"""TPM sealed storage abstraction."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SealedStorage:
    _values: dict[str, str] = field(default_factory=dict)

    def store(self, key: str, value: str) -> None:
        self._values[key] = value

    def load(self, key: str) -> str:
        return self._values[key]
