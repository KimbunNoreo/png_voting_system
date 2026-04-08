from __future__ import annotations

import unittest

from key_management.key_escrow import KeyEscrow
from key_management.shamir_secret_sharing import recover_secret, split_secret


class KeyManagementTests(unittest.TestCase):
    def test_secret_split_and_recover(self) -> None:
        shares = split_secret("secret-value", shares=3)
        self.assertEqual(recover_secret(shares[:2], threshold=2), "secret-value")

    def test_escrow_stores_and_retrieves_shares(self) -> None:
        escrow = KeyEscrow()
        shares = split_secret("key-material", shares=3)
        escrow.escrow("kid-1", shares)
        self.assertEqual(escrow.retrieve("kid-1"), shares)


if __name__ == "__main__":
    unittest.main()
