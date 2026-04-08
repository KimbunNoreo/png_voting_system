from __future__ import annotations
from services.voting_service.crypto.crypto_provider import Phase1CryptoProvider
from services.voting_service.models.vote import Vote
class EncryptionService:
    def __init__(self, crypto_provider: Phase1CryptoProvider | None = None) -> None:
        self.crypto_provider = crypto_provider or Phase1CryptoProvider()
    def encrypt_vote(self, *, vote_id: str, election_id: str, ballot_id: str, selections: dict[str, object], device_id: str, device_signature: str, token_hash: str, recipient_public_key_pem: str, kid: str) -> Vote:
        envelope = self.crypto_provider.encrypt_vote_payload(selections, recipient_public_key_pem)
        return Vote.create(vote_id=vote_id, election_id=election_id, ballot_id=ballot_id, encrypted_vote=envelope["encrypted_vote"], encrypted_key=envelope["encrypted_key"], iv=envelope["iv"], tag=envelope["tag"], device_id=device_id, device_signature=device_signature, token_hash=token_hash, kid=kid)