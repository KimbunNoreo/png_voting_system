from __future__ import annotations

import unittest

from services.voting_service.crypto.phase1_standard import Phase1StandardCrypto


class EncryptionPhase1Tests(unittest.TestCase):
    def test_encrypt_and_decrypt_round_trip(self) -> None:
        crypto = Phase1StandardCrypto()
        private_key = crypto.generate_rsa_private_key()
        private_pem = crypto.serialize_private_key(private_key)
        public_pem = crypto.serialize_public_key(private_key.public_key())
        envelope = crypto.encrypt({"choice": "candidate-a"}, public_pem)
        plaintext = crypto.decrypt(envelope, private_pem)
        self.assertEqual(plaintext["choice"], "candidate-a")


if __name__ == "__main__":
    unittest.main()
