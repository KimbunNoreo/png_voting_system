"""In-memory metrics for NID client instrumentation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NIDClientMetrics:
    verify_calls: int = 0
    lookup_calls: int = 0
    enroll_calls: int = 0
    error_count: int = 0

    def record_verify(self) -> None:
        self.verify_calls += 1

    def record_lookup(self) -> None:
        self.lookup_calls += 1

    def record_enroll(self) -> None:
        self.enroll_calls += 1

    def record_error(self) -> None:
        self.error_count += 1