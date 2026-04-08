from __future__ import annotations

from pathlib import Path
import unittest


class DocsAlignmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.readme = Path("README.md").read_text(encoding="utf-8")
        self.offline_sync_doc = Path("docs/offline_sync_service_api.md").read_text(encoding="utf-8")

    def test_readme_mentions_current_evidence_and_compliance_endpoints(self) -> None:
        for endpoint in (
            "/api/v1/vote/compliance/report",
            "/api/v1/vote/compliance/offline-sync-evidence",
            "/api/v1/offline-sync/operations/export",
            "/api/v1/offline-sync/operations/evidence-bundle",
        ):
            self.assertIn(endpoint, self.readme)

    def test_offline_sync_operator_doc_mentions_current_operation_endpoints(self) -> None:
        for endpoint in (
            "/api/v1/offline-sync/operations",
            "/api/v1/offline-sync/operations/export",
            "/api/v1/offline-sync/operations/evidence-bundle",
            "/api/v1/offline-sync/status",
        ):
            self.assertIn(endpoint, self.offline_sync_doc)


if __name__ == "__main__":
    unittest.main()
