from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
