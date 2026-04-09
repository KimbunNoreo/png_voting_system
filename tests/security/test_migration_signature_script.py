from __future__ import annotations

import unittest

from scripts.rotate_keys import rotate_signing_key
from scripts.sign_migration import sign_manifest
from scripts.verify_migration import verify_manifest


class MigrationScriptTests(unittest.TestCase):
    def test_sign_and_verify_manifest(self) -> None:
        keys = rotate_signing_key()
        manifest = "002_add_ledger"
        signature = sign_manifest(manifest, keys["private_key"])
        self.assertTrue(verify_manifest(manifest, signature, keys["public_key"]))

    def test_sign_manifest_rejects_blank_manifest(self) -> None:
        keys = rotate_signing_key()
        with self.assertRaises(ValueError):
            sign_manifest(" ", keys["private_key"])

    def test_verify_manifest_rejects_blank_signature(self) -> None:
        keys = rotate_signing_key()
        with self.assertRaises(ValueError):
            verify_manifest("002_add_ledger", " ", keys["public_key"])


if __name__ == "__main__":
    unittest.main()
