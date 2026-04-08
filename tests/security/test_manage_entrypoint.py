from __future__ import annotations

import io
import unittest
from unittest.mock import patch

import manage


class ManageEntrypointTests(unittest.TestCase):
    def test_check_phase1_returns_success(self) -> None:
        self.assertEqual(manage.main(["check-phase1"]), 0)

    def test_runserver_dispatches_local_runtime(self) -> None:
        with patch("manage.run_local_demo_server") as run_local_demo_server:
            self.assertEqual(manage.main(["runserver", "127.0.0.1:8123"]), 0)
        run_local_demo_server.assert_called_once_with(host="127.0.0.1", port=8123)

    def test_run_offline_sync_dispatches_service_runtime(self) -> None:
        with patch("manage.run_offline_sync_server") as run_offline_sync_server:
            self.assertEqual(manage.main(["run-offline-sync", "127.0.0.1:8124"]), 0)
        run_offline_sync_server.assert_called_once_with(host="127.0.0.1", port=8124)

    def test_list_endpoints_prints_both_runtime_inventories(self) -> None:
        with patch("sys.stdout", new_callable=io.StringIO) as stdout:
            self.assertEqual(manage.main(["list-endpoints"]), 0)
        output = stdout.getvalue()
        self.assertIn("[local-runtime]", output)
        self.assertIn("Compliance report: GET /api/v1/vote/compliance/report", output)
        self.assertIn("[offline-sync-runtime]", output)
        self.assertIn("Operations Export: GET /api/v1/offline-sync/operations/export", output)

    def test_list_endpoints_markdown_renders_doc_ready_output(self) -> None:
        with patch("sys.stdout", new_callable=io.StringIO) as stdout:
            self.assertEqual(manage.main(["list-endpoints", "--markdown", "offline-sync"]), 0)
        output = stdout.getvalue()
        self.assertIn("### Offline Sync Runtime", output)
        self.assertIn("- `GET /api/v1/offline-sync/operations/export`: Operations Export", output)


if __name__ == "__main__":
    unittest.main()
