"""Key rotation helper using the central crypto implementation."""

from __future__ import annotations

from services.voting_service.crypto.phase1_standard import Phase1StandardCrypto


def rotate_signing_key() -> dict[str, str]:
    crypto = Phase1StandardCrypto()
    private_key = crypto.generate_rsa_private_key()
    return {
        "private_key": crypto.serialize_private_key(private_key),
        "public_key": crypto.serialize_public_key(private_key.public_key()),
    }
