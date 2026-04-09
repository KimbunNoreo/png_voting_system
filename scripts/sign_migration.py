"""Sign migration manifests for audited deployment."""

from __future__ import annotations

from services.voting_service.crypto.crypto_provider import Phase1CryptoProvider


def sign_manifest(manifest: str, private_key_pem: str) -> str:
    manifest_value = str(manifest).strip()
    if not manifest_value:
        raise ValueError("manifest is required")
    private_key_value = str(private_key_pem).strip()
    if not private_key_value:
        raise ValueError("private_key_pem is required")
    return Phase1CryptoProvider().sign_bytes(manifest_value.encode("utf-8"), private_key_value)
