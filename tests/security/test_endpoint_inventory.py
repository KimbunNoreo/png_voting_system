from __future__ import annotations

import unittest

from services.endpoint_inventory import (
    LOCAL_RUNTIME_ENDPOINTS,
    OFFLINE_SYNC_RUNTIME_ENDPOINTS,
    render_inventory_lines,
    render_inventory_markdown,
)


class EndpointInventoryTests(unittest.TestCase):
    def test_local_runtime_inventory_contains_compliance_surface(self) -> None:
        paths = {endpoint.path for endpoint in LOCAL_RUNTIME_ENDPOINTS}
        self.assertIn("/api/v1/vote/compliance/report", paths)
        self.assertIn("/api/v1/vote/compliance/offline-sync-evidence", paths)

    def test_offline_sync_inventory_contains_evidence_surface(self) -> None:
        paths = {endpoint.path for endpoint in OFFLINE_SYNC_RUNTIME_ENDPOINTS}
        self.assertIn("/api/v1/offline-sync/operations/export", paths)
        self.assertIn("/api/v1/offline-sync/operations/evidence-bundle", paths)

    def test_render_inventory_lines_formats_operator_banner(self) -> None:
        lines = render_inventory_lines(OFFLINE_SYNC_RUNTIME_ENDPOINTS)
        self.assertIn("Health: GET /health", lines)
        self.assertIn("Operations Evidence Bundle: GET /api/v1/offline-sync/operations/evidence-bundle", lines)

    def test_render_inventory_markdown_formats_reference_section(self) -> None:
        markdown = render_inventory_markdown("Offline Sync Runtime", OFFLINE_SYNC_RUNTIME_ENDPOINTS)
        self.assertIn("### Offline Sync Runtime", markdown)
        self.assertIn("- `GET /api/v1/offline-sync/status`: Status", markdown)


if __name__ == "__main__":
    unittest.main()
