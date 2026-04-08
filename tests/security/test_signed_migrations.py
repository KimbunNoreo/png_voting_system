from __future__ import annotations

import unittest

from services.voting_service.crypto.phase1_standard import Phase1StandardCrypto
from services.voting_service.services.migration_audit_service import MigrationAuditService


class SignedMigrationTests(unittest.TestCase):
    def test_signed_migration_verification(self) -> None:
        crypto = Phase1StandardCrypto()
        private_key = crypto.generate_rsa_private_key()
        private_pem = crypto.serialize_private_key(private_key)
        public_pem = crypto.serialize_public_key(private_key.public_key())
        manifest = "001_initial"
        signature = crypto.sign(manifest.encode("utf-8"), private_pem)
        result = MigrationAuditService().verify("001_initial", manifest, signature, public_pem, "phase1-signing")
        self.assertTrue(result.verified)


if __name__ == "__main__":
    unittest.main()
