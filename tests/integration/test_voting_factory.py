from __future__ import annotations

from dataclasses import replace
import unittest
from unittest.mock import patch

from config.base import BaseSettings
from services.voting_service.factory import build_voting_dependencies
from services.voting_service.services.result_hash_publisher import SQLiteResultPublicationStore
from services.voting_service.services.ballot_service import SQLiteBallotStore
from services.voting_service.services.device_revocation_service import SQLiteDeviceRevocationStore
from services.voting_service.services.election_state_manager import SQLiteElectionStateStore
from services.voting_service.services.emergency_freeze_service import SQLiteEmergencyFreezeHistoryStore
from services.voting_service.services.rate_limit_enforcer import SQLiteRateLimitStore
from services.voting_service.services.token_consumer import SQLiteUsedTokenStore
from services.voting_service.services.token_replay_detector import SQLiteTokenReplayStore
from services.voting_service.services.vote_repository import SQLiteVoteRepositoryStore
from election_state.control_plane import SQLiteElectionControlStore
from services.audit_service.logger.worm_logger import SQLiteAuditStore
from services.audit_service.settings.audit_settings import AuditSettings
from services.voting_service.settings.app_settings import VotingAppSettings


class VotingFactoryTests(unittest.TestCase):
    def test_factory_uses_durable_sqlite_registries_when_enabled(self) -> None:
        settings = replace(
            BaseSettings(),
            audit_service=AuditSettings(
                use_durable_worm_log=True,
                worm_log_path="data/test_runtime/factory_audit_log.sqlite3",
            ),
            voting_service=VotingAppSettings(
                use_durable_token_registry=True,
                use_durable_result_publications=True,
                use_durable_ballot_registry=True,
                use_durable_election_state=True,
                use_durable_device_revocation_registry=True,
                use_durable_emergency_freeze_history=True,
                use_durable_rate_limits=True,
                use_durable_vote_repository=True,
                use_durable_control_plane=True,
                used_token_registry_path="data/test_runtime/factory_used_tokens.sqlite3",
                token_replay_registry_path="data/test_runtime/factory_token_replay.sqlite3",
                result_publication_path="data/test_runtime/factory_result_publications.sqlite3",
                ballot_registry_path="data/test_runtime/factory_ballots.sqlite3",
                election_state_path="data/test_runtime/factory_election_state.sqlite3",
                device_revocation_path="data/test_runtime/factory_device_revocations.sqlite3",
                emergency_freeze_history_path="data/test_runtime/factory_emergency_freeze.sqlite3",
                rate_limit_path="data/test_runtime/factory_rate_limits.sqlite3",
                vote_repository_path="data/test_runtime/factory_votes.sqlite3",
                control_plane_path="data/test_runtime/factory_control_plane.sqlite3",
                control_plane_phase_audit_path="data/test_runtime/factory_control_plane_phase_audit.sqlite3",
            ),
        )
        with patch("services.voting_service.factory.get_settings", return_value=settings):
            dependencies = build_voting_dependencies()

        self.assertEqual(len(dependencies.audit_logger.entries()), 0)
        self.assertIsInstance(dependencies.audit_logger.store, SQLiteAuditStore)
        self.assertIsInstance(dependencies.ballot_service.store, SQLiteBallotStore)
        self.assertIsInstance(dependencies.election_state_manager.store, SQLiteElectionStateStore)
        self.assertIsInstance(dependencies.device_revocation_service.store, SQLiteDeviceRevocationStore)
        self.assertIsInstance(dependencies.emergency_freeze_service.history_store, SQLiteEmergencyFreezeHistoryStore)
        self.assertIsInstance(dependencies.rate_limit_enforcer.store, SQLiteRateLimitStore)
        self.assertIsInstance(dependencies.vote_repository.store, SQLiteVoteRepositoryStore)
        self.assertIsInstance(dependencies.token_consumer.store, SQLiteUsedTokenStore)
        self.assertIsInstance(dependencies.replay_detector.store, SQLiteTokenReplayStore)
        self.assertIsInstance(dependencies.result_hash_publisher.store, SQLiteResultPublicationStore)
        self.assertIsInstance(dependencies.control_plane.store, SQLiteElectionControlStore)

    def test_factory_uses_in_memory_registries_when_durability_disabled(self) -> None:
        settings = replace(
            BaseSettings(),
            audit_service=AuditSettings(use_durable_worm_log=False),
            voting_service=VotingAppSettings(
                use_durable_token_registry=False,
                use_durable_result_publications=False,
                use_durable_ballot_registry=False,
                use_durable_election_state=False,
                use_durable_device_revocation_registry=False,
                use_durable_emergency_freeze_history=False,
                use_durable_rate_limits=False,
                use_durable_vote_repository=False,
                use_durable_control_plane=False,
            ),
        )
        with patch("services.voting_service.factory.get_settings", return_value=settings):
            dependencies = build_voting_dependencies()

        self.assertEqual(dependencies.ballot_service.store.__class__.__name__, "InMemoryBallotStore")
        self.assertEqual(dependencies.election_state_manager.store.__class__.__name__, "InMemoryElectionStateStore")
        self.assertEqual(dependencies.device_revocation_service.store.__class__.__name__, "InMemoryDeviceRevocationStore")
        self.assertEqual(dependencies.emergency_freeze_service.history_store.__class__.__name__, "InMemoryEmergencyFreezeHistoryStore")
        self.assertEqual(dependencies.rate_limit_enforcer.store.__class__.__name__, "InMemoryRateLimitStore")
        self.assertEqual(dependencies.vote_repository.store.__class__.__name__, "InMemoryVoteRepositoryStore")
        self.assertEqual(dependencies.token_consumer.store.__class__.__name__, "InMemoryUsedTokenStore")
        self.assertEqual(dependencies.replay_detector.store.__class__.__name__, "InMemoryTokenReplayStore")
        self.assertEqual(dependencies.result_hash_publisher.store.__class__.__name__, "InMemoryResultPublicationStore")
        self.assertEqual(dependencies.control_plane.store.__class__.__name__, "InMemoryElectionControlStore")


if __name__ == "__main__":
    unittest.main()
