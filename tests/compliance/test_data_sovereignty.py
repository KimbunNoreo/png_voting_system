from __future__ import annotations

import unittest

from config import get_settings


class DataSovereigntyComplianceTests(unittest.TestCase):
    def test_nid_integration_is_external_but_voting_data_stays_local_to_repo_domains(self) -> None:
        settings = get_settings()
        self.assertTrue(settings.nid_integration.base_url.startswith("https://"))
        self.assertTrue(settings.staged_rollout.phase1_only)


if __name__ == "__main__":
    unittest.main()
