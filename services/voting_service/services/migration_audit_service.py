from __future__ import annotations
from services.voting_service.crypto.crypto_provider import Phase1CryptoProvider
from services.voting_service.models.migration_signature import MigrationSignature
class MigrationAuditService:
    def __init__(self, crypto_provider: Phase1CryptoProvider | None = None) -> None:
        self.crypto_provider = crypto_provider or Phase1CryptoProvider()
    def verify(self, migration_name: str, manifest: str, signature: str, signer_public_key_pem: str, signer_kid: str) -> MigrationSignature:
        verified = self.crypto_provider.verify_bytes(manifest.encode("utf-8"), signature, signer_public_key_pem)
        return MigrationSignature(migration_name=migration_name, signature=signature, signer_kid=signer_kid, verified=verified)