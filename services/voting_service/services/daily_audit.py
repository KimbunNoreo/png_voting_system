from __future__ import annotations
import json
from services.voting_service.crypto.crypto_provider import Phase1CryptoProvider
from services.voting_service.models.daily_audit_hash import DailyAuditHash
from services.voting_service.models.vote import Vote
class DailyAuditService:
    def __init__(self, crypto_provider: Phase1CryptoProvider | None = None) -> None:
        self.crypto_provider = crypto_provider or Phase1CryptoProvider()
    def build(self, device_id: str, day: str, votes: list[Vote]) -> DailyAuditHash:
        canonical = json.dumps([vote.to_dict() for vote in votes], sort_keys=True, default=str)
        return DailyAuditHash(device_id=device_id, day=day, digest=self.crypto_provider.digest(canonical))