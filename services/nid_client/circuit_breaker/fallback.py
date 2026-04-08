"""Fallback policies when NID is unavailable."""

from __future__ import annotations

from dataclasses import dataclass

from services.nid_client.exceptions import NIDUnavailableError


@dataclass(frozen=True)
class KBAMultiPersonFallback:
    required_approvals: int = 2

    def block(self, reason: str) -> None:
        raise NIDUnavailableError(
            f"NID unavailable. Fallback requires KBA plus {self.required_approvals} human approvals: {reason}"
        )