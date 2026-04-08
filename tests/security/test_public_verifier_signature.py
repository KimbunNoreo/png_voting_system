from __future__ import annotations

import unittest

from public_verifier_cli.crypto_verifier import verify_signature
from services.voting_service.crypto.phase1_standard import Phase1StandardCrypto


class PublicVerifierSignatureTests(unittest.TestCase):
    def test_crypto_verifier_accepts_valid_signature(self) -> None:
        crypto = Phase1StandardCrypto()
        private_key = crypto.generate_rsa_private_key()
        private_pem = crypto.serialize_private_key(private_key)
        public_pem = crypto.serialize_public_key(private_key.public_key())
        payload = "signed-payload"
        signature = crypto.sign(payload.encode("utf-8"), private_pem)
        self.assertTrue(verify_signature(payload, signature, public_pem))


if __name__ == "__main__":
    unittest.main()
