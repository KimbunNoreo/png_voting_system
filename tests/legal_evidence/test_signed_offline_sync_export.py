from __future__ import annotations

import json
import unittest

from legal_evidence.signed_offline_sync_export import create_signed_offline_sync_export
from services.voting_service.crypto.crypto_provider import Phase1CryptoProvider
from services.voting_service.crypto.phase1_standard import Phase1StandardCrypto


class SignedOfflineSyncExportTests(unittest.TestCase):
    def test_signed_export_redacts_sensitive_fields_before_signing(self) -> None:
        crypto = Phase1StandardCrypto()
        keypair = crypto.generate_rsa_private_key()
        private_pem = crypto.serialize_private_key(keypair)
        public_pem = crypto.serialize_public_key(keypair.public_key())
        export = create_signed_offline_sync_export(
            [
                {
                    "operation_id": "operation-1",
                    "operator_id": "operator-1",
                    "manifest_digest": "sha256:abc",
                    "conflict_report": {
                        "conflict_count": 1,
                        "decisions": [{"token_hash": "t1", "sub": "citizen-1"}],
                    },
                    "authorization": "Bearer raw-admin-token",
                }
            ],
            private_pem,
        )
        payload = json.loads(export["payload"])
        decision = payload["operations"][0]["conflict_report"]["decisions"][0]
        self.assertEqual(decision["sub"], "[redacted]")
        self.assertEqual(payload["operations"][0]["authorization"], "[redacted]")
        self.assertTrue(
            Phase1CryptoProvider().verify_bytes(export["payload"].encode("utf-8"), export["signature"], public_pem)
        )


if __name__ == "__main__":
    unittest.main()
