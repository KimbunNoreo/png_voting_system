from __future__ import annotations

import unittest

from chaos_testing.sync_failure_injector import inject_sync_failure


class SyncFailureChaosTests(unittest.TestCase):
    def test_sync_failure_requires_recovery(self) -> None:
        result = inject_sync_failure(5)
        self.assertTrue(result["recovery_required"])

    def test_sync_failure_redacts_sensitive_diagnostics(self) -> None:
        result = inject_sync_failure(3, diagnostics={"token": "raw-token", "name": "Sensitive Name"})
        self.assertEqual(result["diagnostics"]["token"], "[redacted]")
        self.assertEqual(result["diagnostics"]["name"], "[redacted]")

    def test_sync_failure_rejects_negative_queue_depth(self) -> None:
        with self.assertRaises(ValueError):
            inject_sync_failure(-1)


if __name__ == "__main__":
    unittest.main()
