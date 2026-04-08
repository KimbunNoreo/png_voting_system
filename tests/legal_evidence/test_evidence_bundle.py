from __future__ import annotations

import unittest

from legal_evidence.evidence_bundle_generator import generate_evidence_bundle


class EvidenceBundleTests(unittest.TestCase):
    def test_bundle_contains_metadata_and_custody(self) -> None:
        bundle = generate_evidence_bundle(
            "case-1",
            [{"artifact_id": "a1", "kind": "audit"}],
            "official-1",
        )
        self.assertEqual(bundle.case_id, "case-1")
        self.assertEqual(bundle.artifacts[0]["metadata"]["case_id"], "case-1")
        self.assertEqual(bundle.custody_events[0].actor, "official-1")

    def test_bundle_redacts_sensitive_artifact_fields(self) -> None:
        bundle = generate_evidence_bundle(
            "case-2",
            [
                {
                    "artifact_id": "a2",
                    "kind": "audit",
                    "name": "Sensitive Name",
                    "sub": "citizen-123",
                    "nested": {"address": "Sensitive Address"},
                }
            ],
            "official-2",
        )
        artifact = bundle.artifacts[0]
        self.assertEqual(artifact["name"], "[redacted]")
        self.assertEqual(artifact["sub"], "[redacted]")
        self.assertEqual(artifact["nested"]["address"], "[redacted]")


if __name__ == "__main__":
    unittest.main()
