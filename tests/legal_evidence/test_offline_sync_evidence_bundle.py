from __future__ import annotations

import unittest

from legal_evidence.evidence_bundle_generator import generate_offline_sync_evidence_bundle
from services.voting_service.crypto.phase1_standard import Phase1StandardCrypto


class OfflineSyncEvidenceBundleTests(unittest.TestCase):
    def test_bundle_contains_signed_offline_sync_artifact_and_custody(self) -> None:
        crypto = Phase1StandardCrypto()
        private_pem = crypto.serialize_private_key(crypto.generate_rsa_private_key())
        bundle = generate_offline_sync_evidence_bundle(
            case_id="case-offline-1",
            operations=[
                {
                    "operation_id": "operation-1",
                    "operator_id": "operator-1",
                    "device_id": "device-1",
                    "manifest_digest": "sha256:abc",
                    "conflict_report": {"conflict_count": 1, "decisions": [{"token_hash": "t1", "sub": "citizen-1"}]},
                }
            ],
            actor="official-1",
            signing_key_pem=private_pem,
        )
        self.assertEqual(bundle.case_id, "case-offline-1")
        self.assertEqual(bundle.artifacts[0]["kind"], "offline_sync_export")
        self.assertEqual(bundle.artifacts[0]["metadata"]["artifact_role"], "offline_sync_reconciliation")
        self.assertEqual(bundle.artifacts[0]["operations"][0]["conflict_report"]["decisions"][0]["sub"], "[redacted]")
        self.assertEqual(bundle.custody_events[0].action, "offline_sync_export_signed")
        self.assertEqual(bundle.custody_events[1].action, "bundle_created")
        self.assertTrue(bundle.artifacts[0]["signature"])


if __name__ == "__main__":
    unittest.main()
