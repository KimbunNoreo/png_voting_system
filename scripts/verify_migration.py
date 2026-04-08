"""Verify signed migration manifests."""

from __future__ import annotations

from services.voting_service.crypto.crypto_provider import Phase1CryptoProvider


def verify_manifest(manifest: str, signature: str, public_key_pem: str) -> bool:
    return Phase1CryptoProvider().verify_bytes(manifest.encode("utf-8"), signature, public_key_pem)
