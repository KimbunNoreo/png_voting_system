from __future__ import annotations

from dataclasses import replace
import unittest
from unittest.mock import patch

from config.base import BaseSettings
from services.audit_service import WORMLogger
from services.offline_sync_service.factory import build_offline_sync_dependencies
from services.offline_sync_service.settings import SyncSettings
from human_factors.multi_person_auth.approval_tracking import SQLiteApprovalStore
from services.offline_sync_service.operation_history import SQLiteOfflineSyncOperationHistoryStore


class OfflineSyncFactoryTests(unittest.TestCase):
    def test_factory_uses_durable_approval_tracker_when_enabled(self) -> None:
        settings = replace(
            BaseSettings(),
            offline_sync_service=SyncSettings(
                use_durable_approval_tracker=True,
                approval_tracker_path="data/test_runtime/offline_sync_factory_approvals.sqlite3",
                use_durable_operation_history=True,
                operation_history_path="data/test_runtime/offline_sync_factory_operations.sqlite3",
            ),
        )
        with patch("services.offline_sync_service.factory.get_settings", return_value=settings):
            dependencies = build_offline_sync_dependencies(audit_logger=WORMLogger())
        self.assertIsInstance(dependencies.approval_tracker.store, SQLiteApprovalStore)
        self.assertIsInstance(dependencies.operation_history.store, SQLiteOfflineSyncOperationHistoryStore)
        self.assertIs(dependencies.operator_api.approval_tracker, dependencies.approval_tracker)
        self.assertIs(dependencies.operator_api.operation_log, dependencies.operation_history)
        self.assertIsNotNone(dependencies.audit_logger)

    def test_factory_uses_in_memory_approval_tracker_when_disabled(self) -> None:
        settings = replace(
            BaseSettings(),
            offline_sync_service=SyncSettings(
                use_durable_approval_tracker=False,
                use_durable_operation_history=False,
            ),
        )
        with patch("services.offline_sync_service.factory.get_settings", return_value=settings):
            dependencies = build_offline_sync_dependencies()
        self.assertEqual(dependencies.approval_tracker.store.__class__.__name__, "InMemoryApprovalStore")
        self.assertEqual(
            dependencies.operation_history.store.__class__.__name__,
            "InMemoryOfflineSyncOperationHistoryStore",
        )

    def test_factory_can_force_in_memory_for_runtime_isolation(self) -> None:
        settings = replace(
            BaseSettings(),
            offline_sync_service=SyncSettings(
                use_durable_approval_tracker=True,
                approval_tracker_path="data/test_runtime/offline_sync_factory_forced.sqlite3",
                use_durable_operation_history=True,
                operation_history_path="data/test_runtime/offline_sync_factory_forced_operations.sqlite3",
            ),
        )
        with patch("services.offline_sync_service.factory.get_settings", return_value=settings):
            dependencies = build_offline_sync_dependencies(force_in_memory=True)
        self.assertEqual(dependencies.approval_tracker.store.__class__.__name__, "InMemoryApprovalStore")
        self.assertEqual(
            dependencies.operation_history.store.__class__.__name__,
            "InMemoryOfflineSyncOperationHistoryStore",
        )


if __name__ == "__main__":
    unittest.main()
