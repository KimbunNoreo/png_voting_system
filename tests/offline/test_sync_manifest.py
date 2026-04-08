from __future__ import annotations

import unittest

from services.offline_sync_service.sync.sync_manifest import build_sync_manifest, verify_sync_manifest
from services.voting_service.crypto.phase1_standard import Phase1StandardCrypto


class SyncManifestTests(unittest.TestCase):
    def test_sync_manifest_signs_and_verifies(self) -> None:
        crypto = Phase1StandardCrypto()
        private_key = crypto.generate_rsa_private_key()
        private_pem = crypto.serialize_private_key(private_key)
        public_pem = crypto.serialize_public_key(private_key.public_key())
        manifest = build_sync_manifest(
            "device-1",
            [
                {"token_hash": "t2", "created_at": "2026-04-07T00:01:00Z"},
                {"token_hash": "t1", "created_at": "2026-04-07T00:00:00Z"},
            ],
            private_pem,
        )
        self.assertEqual(manifest.token_hashes, ("t1", "t2"))
        self.assertTrue(verify_sync_manifest(manifest, public_pem))


if __name__ == "__main__":
    unittest.main()
