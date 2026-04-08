"""Verification response models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class VerificationResponse:
    verification_token: str
    token_id: str
    eligible: bool
    expires_at: datetime
    signature_kid: str