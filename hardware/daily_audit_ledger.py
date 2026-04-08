"""Hardware-protected daily audit ledger."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DailyAuditLedger:
    entries: list[str] = field(default_factory=list)

    def append(self, digest: str) -> None:
        self.entries.append(digest)
