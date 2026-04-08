"""Simple circuit breaker for external NID requests."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from services.nid_client.exceptions import NIDUnavailableError


@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    reset_timeout_seconds: int = 60
    failure_count: int = 0
    opened_at: datetime | None = None

    def before_request(self) -> None:
        if self.opened_at is None:
            return
        if datetime.now(timezone.utc) - self.opened_at >= timedelta(seconds=self.reset_timeout_seconds):
            self.failure_count = 0
            self.opened_at = None
            return
        raise NIDUnavailableError("NID circuit breaker is open")

    def record_success(self) -> None:
        self.failure_count = 0
        self.opened_at = None

    def record_failure(self) -> None:
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.opened_at = datetime.now(timezone.utc)