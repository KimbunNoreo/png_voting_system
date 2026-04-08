from __future__ import annotations

import unittest

from human_factors.multi_person_auth.approval_tracking import ApprovalTracker
from services.audit_service import WORMLogger
from services.offline_sync_service.api.operator import OfflineSyncOperatorAPI
from services.offline_sync_service.sync.engine import SyncEngine
from services.voting_service.crypto.phase1_standard import Phase1StandardCrypto


class OfflineSyncOperatorAPITests(unittest.TestCase):
    def test_operator_api_stages_and_reports_queue_state(self) -> None:
        logger = WORMLogger()
        api = OfflineSyncOperatorAPI(SyncEngine(), audit_logger=logger, approval_tracker=ApprovalTracker())
        stage_result = api.stage_record(
            {
                "token_hash": "t1",
                "created_at": "2026-04-08T00:00:00Z",
                "sub": "citizen-1",
            },
            operator_id="operator-1",
        )
        self.assertEqual(stage_result["queue_depth"], 1)
        self.assertEqual(stage_result["record"]["sub"], "[redacted]")
        status = api.queue_status(operator_id="operator-1")
        self.assertEqual(status["queue_depth"], 1)
        self.assertEqual(status["queued_records"][0]["sub"], "[redacted]")
        self.assertEqual(logger.entries()[-2].event_type, "offline_sync_record_staged")
        self.assertEqual(logger.entries()[-2].payload["operator_id"], "operator-1")
        self.assertEqual(logger.entries()[-1].event_type, "offline_sync_queue_inspected")

    def test_operator_api_flush_returns_verified_manifest(self) -> None:
        logger = WORMLogger()
        tracker = ApprovalTracker()
        api = OfflineSyncOperatorAPI(SyncEngine(), audit_logger=logger, approval_tracker=tracker)
        api.stage_record({"token_hash": "t2", "created_at": "2026-04-08T00:00:00Z"}, operator_id="operator-2")
        crypto = Phase1StandardCrypto()
        keypair = crypto.generate_rsa_private_key()
        private_pem = crypto.serialize_private_key(keypair)
        public_pem = crypto.serialize_public_key(keypair.public_key())
        result = api.flush(
            remote_records=[{"token_hash": "t2", "created_at": "2026-04-08T00:01:00Z"}],
            device_id="device-1",
            private_key_pem=private_pem,
            public_key_pem=public_pem,
            operator_id="operator-2",
            approvers=("official-1", "official-2"),
        )
        self.assertEqual(result["queue_depth"], 0)
        self.assertTrue(result["manifest_valid"])
        self.assertEqual(result["artifacts"]["conflict_report"]["conflict_count"], 1)
        self.assertEqual(logger.entries()[-1].event_type, "offline_sync_flushed")
        self.assertEqual(logger.entries()[-1].payload["operator_id"], "operator-2")
        self.assertTrue(logger.entries()[-1].payload["manifest_valid"])
        self.assertEqual(len(api.approval_history()), 2)
        self.assertEqual(len(api.operation_history()), 1)
        self.assertEqual(api.operation_history()[0]["operator_id"], "operator-2")
        self.assertEqual(api.operation_history()[0]["conflict_count"], 1)

    def test_operator_api_rejects_conflict_flush_without_two_approvers(self) -> None:
        logger = WORMLogger()
        api = OfflineSyncOperatorAPI(SyncEngine(), audit_logger=logger, approval_tracker=ApprovalTracker())
        api.stage_record({"token_hash": "t3", "created_at": "2026-04-08T00:00:00Z"}, operator_id="operator-3")
        crypto = Phase1StandardCrypto()
        keypair = crypto.generate_rsa_private_key()
        private_pem = crypto.serialize_private_key(keypair)
        public_pem = crypto.serialize_public_key(keypair.public_key())
        with self.assertRaises(ValueError):
            api.flush(
                remote_records=[{"token_hash": "t3", "created_at": "2026-04-08T00:01:00Z"}],
                device_id="device-1",
                private_key_pem=private_pem,
                public_key_pem=public_pem,
                operator_id="operator-3",
                approvers=("official-1",),
            )
        self.assertEqual(logger.entries()[-1].event_type, "offline_sync_flush_rejected")
        self.assertEqual(logger.entries()[-1].payload["required_approvals"], 2)

    def test_operator_api_exposes_approval_history_for_operation(self) -> None:
        tracker = ApprovalTracker()
        api = OfflineSyncOperatorAPI(SyncEngine(), approval_tracker=tracker)
        api.stage_record({"token_hash": "t4", "created_at": "2026-04-08T00:00:00Z"})
        crypto = Phase1StandardCrypto()
        keypair = crypto.generate_rsa_private_key()
        private_pem = crypto.serialize_private_key(keypair)
        public_pem = crypto.serialize_public_key(keypair.public_key())
        api.flush(
            remote_records=[{"token_hash": "t4", "created_at": "2026-04-08T00:01:00Z"}],
            device_id="device-1",
            private_key_pem=private_pem,
            public_key_pem=public_pem,
            approvers=("official-1", "official-2"),
        )
        approvals = api.approval_history()
        self.assertEqual(len(approvals), 2)
        self.assertEqual(approvals[0]["approver"], "official-1")
        operations = api.operation_history()
        self.assertEqual(len(operations), 1)
        self.assertEqual(operations[0]["device_id"], "device-1")


if __name__ == "__main__":
    unittest.main()
