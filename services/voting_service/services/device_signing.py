from __future__ import annotations
import json
from services.voting_service.crypto.crypto_provider import Phase1CryptoProvider
from services.voting_service.models.device_vote_signature import DeviceVoteSignature
class DeviceSigningService:
    def __init__(self, crypto_provider: Phase1CryptoProvider | None = None) -> None:
        self.crypto_provider = crypto_provider or Phase1CryptoProvider()
    def sign_vote(self, vote_id: str, device_id: str, payload: dict[str, object], private_key_pem: str) -> DeviceVoteSignature:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        signature = self.crypto_provider.sign_bytes(canonical, private_key_pem)
        digest = self.crypto_provider.digest(canonical.decode("utf-8"))
        return DeviceVoteSignature(vote_id=vote_id, device_id=device_id, signature=signature, digest=digest)