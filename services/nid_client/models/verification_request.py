"""Verification request models."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class VerificationRequest:
    citizen_reference: str
    biometric_assertion: str
    device_id: str
    election_id: str

    def to_payload(self) -> dict[str, str]:
        return asdict(self)