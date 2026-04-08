"""Enrollment request model for NID staging and test flows."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class EnrollmentRequest:
    citizen_reference: str
    enrollment_payload: dict[str, object]

    def to_payload(self) -> dict[str, object]:
        return asdict(self)