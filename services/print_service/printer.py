"""Secure printer abstraction."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SecurePrinter:
    printer_name: str
    printed_jobs: list[str] = field(default_factory=list)

    def print_document(self, document: str) -> str:
        self.printed_jobs.append(document)
        return document
