from __future__ import annotations

import json
import unittest

from legal_evidence.signed_audit_export import create_signed_audit_export
from services.voting_service.crypto.phase1_standard import Phase1StandardCrypto


class SignedAuditExportTests(unittest.TestCase):
    def test_signed_export_redacts_sensitive_fields_before_signing(self) -> None:
        crypto = Phase1StandardCrypto()
        private_pem = crypto.serialize_private_key(crypto.generate_rsa_private_key())
        export = create_signed_audit_export(
            json.dumps(
                {
                    "event_type": "vote_cast",
                    "payload": {
                        "election_id": "election-2026",
                        "name": "Sensitive Name",
                        "token": "raw-token",
                    },
                }
            ),
            private_pem,
        )
        payload = json.loads(export["payload"])
        self.assertEqual(payload["payload"]["name"], "[redacted]")
        self.assertEqual(payload["payload"]["token"], "[redacted]")
        self.assertEqual(payload["payload"]["election_id"], "election-2026")
        self.assertTrue(export["signature"])


if __name__ == "__main__":
    unittest.main()
