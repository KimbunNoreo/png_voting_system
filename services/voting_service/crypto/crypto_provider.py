"""Single crypto entry point for the voting system."""
from __future__ import annotations
import hashlib
from typing import Any
from services.voting_service.crypto.phase1_standard import Phase1StandardCrypto
class Phase1CryptoProvider:
    def __init__(self) -> None:
        self._impl = Phase1StandardCrypto()
    def encrypt_vote_payload(self, payload: dict[str, Any], public_key_pem: str) -> dict[str, str]:
        return self._impl.encrypt(payload, public_key_pem)
    def decrypt_vote_payload(self, envelope: dict[str, str], private_key_pem: str) -> dict[str, Any]:
        return self._impl.decrypt(envelope, private_key_pem)
    def sign_bytes(self, payload: bytes, private_key_pem: str) -> str:
        return self._impl.sign(payload, private_key_pem)
    def verify_bytes(self, payload: bytes, signature: str, public_key_pem: str) -> bool:
        return self._impl.verify(payload, signature, public_key_pem)
    def hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()
    def digest(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()