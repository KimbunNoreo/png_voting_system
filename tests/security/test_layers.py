from __future__ import annotations

import unittest

from config import get_settings


class SecurityLayerTests(unittest.TestCase):
    def test_phase1_security_controls_enabled(self) -> None:
        settings = get_settings()
        self.assertTrue(settings.security.require_mtls_between_services)
        self.assertFalse(settings.ai_mode.enabled)
        self.assertTrue(settings.staged_rollout.phase1_only)
        self.assertTrue(settings.audit_service.use_durable_worm_log)
        self.assertTrue(settings.voting_service.use_durable_ballot_registry)
        self.assertTrue(settings.voting_service.use_durable_election_state)
        self.assertTrue(settings.voting_service.use_durable_device_revocation_registry)
        self.assertTrue(settings.voting_service.use_durable_emergency_freeze_history)
        self.assertTrue(settings.voting_service.use_durable_rate_limits)
        self.assertTrue(settings.voting_service.use_durable_vote_repository)
        self.assertTrue(settings.voting_service.use_durable_token_registry)
        self.assertTrue(settings.voting_service.use_durable_result_publications)
        self.assertTrue(settings.voting_service.use_durable_control_plane)
        self.assertTrue(settings.offline_sync_service.use_durable_approval_tracker)


if __name__ == "__main__":
    unittest.main()
