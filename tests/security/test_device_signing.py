from __future__ import annotations

import json
import unittest

from services.voting_service.crypto.crypto_provider import Phase1CryptoProvider
from services.voting_service.crypto.phase1_standard import Phase1StandardCrypto
from services.voting_service.services.device_signing import DeviceSigningService


class DeviceSigningTests(unittest.TestCase):
    def test_device_signature_verifies(self) -> None:
        crypto = Phase1StandardCrypto()
        private_key = crypto.generate_rsa_private_key()
        private_pem = crypto.serialize_private_key(private_key)
        public_pem = crypto.serialize_public_key(private_key.public_key())
        payload = {"vote": "candidate-a"}
        signed = DeviceSigningService().sign_vote("vote-1", "device-1", payload, private_pem)
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.assertTrue(Phase1CryptoProvider().verify_bytes(canonical, signed.signature, public_pem))


if __name__ == "__main__":
    unittest.main()
