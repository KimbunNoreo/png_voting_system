"""Independent signature verification helpers."""

from __future__ import annotations

from services.voting_service.crypto.crypto_provider import Phase1CryptoProvider


def verify_signature(payload: str, signature: str, public_key_pem: str) -> bool:
    return Phase1CryptoProvider().verify_bytes(payload.encode("utf-8"), signature, public_key_pem)
