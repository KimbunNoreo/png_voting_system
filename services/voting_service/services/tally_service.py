from __future__ import annotations
from collections import Counter
from services.voting_service.crypto.crypto_provider import Phase1CryptoProvider
from services.voting_service.models.vote import Vote
class TallyService:
    def __init__(self, crypto_provider: Phase1CryptoProvider | None = None) -> None:
        self.crypto_provider = crypto_provider or Phase1CryptoProvider()
    def tally(self, votes: list[Vote], private_key_pem: str) -> dict[str, int]:
        totals: Counter[str] = Counter()
        for vote in votes:
            payload = self.crypto_provider.decrypt_vote_payload({"encrypted_vote": vote.encrypted_vote, "encrypted_key": vote.encrypted_key, "iv": vote.iv, "tag": vote.tag}, private_key_pem)
            selections = payload.get("selections", {})
            if not isinstance(selections, dict):
                raise ValueError("Decrypted vote payload is missing selections")
            for candidate in selections.values():
                totals[str(candidate)] += 1
        return dict(totals)
