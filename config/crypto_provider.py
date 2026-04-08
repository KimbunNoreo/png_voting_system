"""Configuration-facing crypto provider factory."""

from __future__ import annotations

from services.voting_service.crypto.crypto_provider import Phase1CryptoProvider


def build_crypto_provider() -> Phase1CryptoProvider:
    """Return the Phase 1 crypto provider mandated by deployment policy."""

    return Phase1CryptoProvider()