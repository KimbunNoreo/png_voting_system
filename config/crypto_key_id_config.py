"""Key identifier configuration for crypto material selection."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CryptoKeyConfig:
    """Maps key identifiers to active Phase 1 crypto profiles."""

    active_kid: str = "phase1-default"
    signature_kid: str = "phase1-signing"
    encryption_kid: str = "phase1-encryption"
    algorithm: str = "RS256"
    scheme_version: str = "1.0.0"