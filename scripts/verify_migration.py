"""Verify signed migration manifests."""

from __future__ import annotations

from services.voting_service.crypto.crypto_provider import Phase1CryptoProvider


def verify_manifest(manifest: str, signature: str, public_key_pem: str) -> bool:
    manifest_value = str(manifest).strip()
    if not manifest_value:
        raise ValueError("manifest is required")
    signature_value = str(signature).strip()
    if not signature_value:
        raise ValueError("signature is required")
    public_key_value = str(public_key_pem).strip()
    if not public_key_value:
        raise ValueError("public_key_pem is required")
    return Phase1CryptoProvider().verify_bytes(manifest_value.encode("utf-8"), signature_value, public_key_value)
