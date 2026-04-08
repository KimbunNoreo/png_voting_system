"""Sign migration manifests for audited deployment."""

from __future__ import annotations

from services.voting_service.crypto.crypto_provider import Phase1CryptoProvider


def sign_manifest(manifest: str, private_key_pem: str) -> str:
    return Phase1CryptoProvider().sign_bytes(manifest.encode("utf-8"), private_key_pem)
