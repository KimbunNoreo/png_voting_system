"""Encrypted local vote store abstraction."""

from __future__ import annotations

from dataclasses import dataclass, field

from services.audit_service.payload_sanitizer import sanitize_audit_payload


@dataclass
class EncryptedStore:
    """In-memory SQLCipher-like store used by the offline sync service."""

    encryption_key_id: str = "phase1-encryption"
    _records: list[dict[str, object]] = field(default_factory=list)

    def insert(self, record: dict[str, object]) -> None:
        self._records.append(sanitize_audit_payload(record))

    def fetch_all(self) -> list[dict[str, object]]:
        return [record.copy() for record in self._records]

    def clear(self) -> None:
        self._records.clear()
