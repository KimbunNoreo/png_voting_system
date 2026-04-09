from __future__ import annotations

from services.voting_service.crypto.crypto_provider import Phase1CryptoProvider
from services.voting_service.models.migration_signature import MigrationSignature


class MigrationAuditService:
    def __init__(self, crypto_provider: Phase1CryptoProvider | None = None) -> None:
        self.crypto_provider = crypto_provider or Phase1CryptoProvider()

    @staticmethod
    def _require_non_empty(value: str, field_name: str) -> str:
        normalized = str(value).strip()
        if not normalized:
            raise ValueError(f"{field_name} is required")
        return normalized

    def verify(
        self,
        migration_name: str,
        manifest: str,
        signature: str,
        signer_public_key_pem: str,
        signer_kid: str,
    ) -> MigrationSignature:
        migration_name_value = self._require_non_empty(migration_name, "migration_name")
        manifest_value = self._require_non_empty(manifest, "manifest")
        signature_value = self._require_non_empty(signature, "signature")
        signer_public_key_pem_value = self._require_non_empty(signer_public_key_pem, "signer_public_key_pem")
        signer_kid_value = self._require_non_empty(signer_kid, "signer_kid")

        verified = self.crypto_provider.verify_bytes(
            manifest_value.encode("utf-8"),
            signature_value,
            signer_public_key_pem_value,
        )
        return MigrationSignature(
            migration_name=migration_name_value,
            signature=signature_value,
            signer_kid=signer_kid_value,
            verified=verified,
        )
