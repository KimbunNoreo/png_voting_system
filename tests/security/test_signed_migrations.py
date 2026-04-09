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

    def test_signed_migration_verification_fails_with_wrong_key(self) -> None:
        crypto = Phase1StandardCrypto()
        signing_private = crypto.generate_rsa_private_key()
        wrong_private = crypto.generate_rsa_private_key()
        signing_private_pem = crypto.serialize_private_key(signing_private)
        wrong_public_pem = crypto.serialize_public_key(wrong_private.public_key())
        manifest = "001_initial"
        signature = crypto.sign(manifest.encode("utf-8"), signing_private_pem)
        result = MigrationAuditService().verify("001_initial", manifest, signature, wrong_public_pem, "phase1-signing")
        self.assertFalse(result.verified)

    def test_signed_migration_verification_rejects_blank_manifest(self) -> None:
        crypto = Phase1StandardCrypto()
        private_key = crypto.generate_rsa_private_key()
        public_pem = crypto.serialize_public_key(private_key.public_key())
        with self.assertRaises(ValueError):
            MigrationAuditService().verify("001_initial", " ", "sig", public_pem, "phase1-signing")


if __name__ == "__main__":
    unittest.main()
