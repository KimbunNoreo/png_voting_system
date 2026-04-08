from __future__ import annotations

import unittest

from public_verifier_cli.download_public_data import fetch_public_data


class PublicDownloadTests(unittest.TestCase):
    def test_download_payload_redacts_sensitive_metadata(self) -> None:
        payload = fetch_public_data(
            "result-hash",
            "audit-digest",
            metadata={
                "published_by": "observer-board",
                "sub": "citizen-1",
                "authorization": "Bearer secret",
                "nested": {"address": "Sensitive Address"},
            },
        )
        self.assertEqual(payload["result_hash"], "result-hash")
        self.assertEqual(payload["audit_digest"], "audit-digest")
        self.assertEqual(payload["metadata"]["published_by"], "observer-board")
        self.assertEqual(payload["metadata"]["sub"], "[redacted]")
        self.assertEqual(payload["metadata"]["authorization"], "[redacted]")
        self.assertEqual(payload["metadata"]["nested"]["address"], "[redacted]")


if __name__ == "__main__":
    unittest.main()
