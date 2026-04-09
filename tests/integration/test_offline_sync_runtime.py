from __future__ import annotations

import json
import unittest

from services.audit_service import WORMLogger
from services.offline_sync_service.factory import build_offline_sync_dependencies
from services.offline_sync_service.runtime import OfflineSyncServiceRuntime
from services.voting_service.crypto.crypto_provider import Phase1CryptoProvider


class OfflineSyncRuntimeTests(unittest.TestCase):
    def build_runtime(self) -> OfflineSyncServiceRuntime:
        return OfflineSyncServiceRuntime(
            dependencies=build_offline_sync_dependencies(
                audit_logger=WORMLogger(),
                force_in_memory=True,
            )
        )

    def test_health_endpoint_returns_ok(self) -> None:
        runtime = self.build_runtime()
        status_code, payload = runtime.dispatch("GET", "/health", headers={})
        self.assertEqual(status_code, 200)
        self.assertEqual(payload["service"], "offline_sync_service")

    def test_ready_endpoint_reports_runtime_state(self) -> None:
        runtime = self.build_runtime()
        status_code, payload = runtime.dispatch("GET", "/ready", headers={})
        self.assertEqual(status_code, 200)
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["service"], "offline_sync_service")
        self.assertIn("approval_store", payload)
        self.assertIn("operation_store", payload)
        self.assertEqual(payload["queue_depth"], 0)

    def test_offline_sync_runtime_stages_and_flushes_records(self) -> None:
        runtime = self.build_runtime()
        status_code, payload = runtime.dispatch(
            "POST",
            "/api/v1/offline-sync/stage",
            headers={"Authorization": "Bearer admin-operator-1"},
            body=json.dumps({"record": {"token_hash": "t1", "created_at": "2026-04-08T00:00:00Z", "sub": "citizen-1"}}),
        )
        self.assertEqual(status_code, 200)
        self.assertEqual(payload["record"]["sub"], "[redacted]")

        status_code, payload = runtime.dispatch(
            "POST",
            "/api/v1/offline-sync/flush",
            headers={"Authorization": "Bearer admin-operator-1"},
            body=json.dumps(
                {
                    "device_id": "device-1",
                    "remote_records": [{"token_hash": "t1", "created_at": "2026-04-08T00:01:00Z"}],
                    "approvers": ["official-1", "official-2"],
                }
            ),
        )
        self.assertEqual(status_code, 200)
        self.assertTrue(payload["manifest_valid"])
        self.assertEqual(payload["artifacts"]["conflict_report"]["conflict_count"], 1)

    def test_offline_sync_runtime_exposes_approval_history(self) -> None:
        runtime = self.build_runtime()
        runtime.dispatch(
            "POST",
            "/api/v1/offline-sync/stage",
            headers={"Authorization": "Bearer admin-operator-2"},
            body=json.dumps({"record": {"token_hash": "t2", "created_at": "2026-04-08T00:00:00Z"}}),
        )
        _, flush_payload = runtime.dispatch(
            "POST",
            "/api/v1/offline-sync/flush",
            headers={"Authorization": "Bearer admin-operator-2"},
            body=json.dumps(
                {
                    "device_id": "device-1",
                    "remote_records": [{"token_hash": "t2", "created_at": "2026-04-08T00:01:00Z"}],
                    "approvers": ["official-1", "official-2"],
                }
            ),
        )
        operation_id = runtime.dependencies.operator_api.approval_history()[0]["operation_id"]
        status_code, payload = runtime.dispatch(
            "GET",
            "/api/v1/offline-sync/approvals",
            headers={"Authorization": "Bearer admin-operator-2"},
            body=json.dumps({"operation_id": operation_id}),
        )
        self.assertEqual(status_code, 200)
        self.assertEqual(len(payload["approvals"]), 2)

    def test_offline_sync_runtime_exposes_operation_history(self) -> None:
        runtime = self.build_runtime()
        runtime.dispatch(
            "POST",
            "/api/v1/offline-sync/stage",
            headers={"Authorization": "Bearer admin-operator-4"},
            body=json.dumps({"record": {"token_hash": "t4", "created_at": "2026-04-08T00:00:00Z"}}),
        )
        runtime.dispatch(
            "POST",
            "/api/v1/offline-sync/flush",
            headers={"Authorization": "Bearer admin-operator-4"},
            body=json.dumps(
                {
                    "device_id": "device-1",
                    "remote_records": [{"token_hash": "t4", "created_at": "2026-04-08T00:01:00Z"}],
                    "approvers": ["official-1", "official-2"],
                }
            ),
        )
        status_code, payload = runtime.dispatch(
            "GET",
            "/api/v1/offline-sync/operations",
            headers={"Authorization": "Bearer admin-operator-4"},
        )
        self.assertEqual(status_code, 200)
        self.assertEqual(len(payload["operations"]), 1)
        self.assertEqual(payload["operations"][0]["operator_id"], "operator-4")
        self.assertTrue(payload["operations"][0]["manifest_valid"])

    def test_offline_sync_runtime_exports_signed_operation_history(self) -> None:
        runtime = self.build_runtime()
        runtime.dispatch(
            "POST",
            "/api/v1/offline-sync/stage",
            headers={"Authorization": "Bearer admin-operator-5"},
            body=json.dumps({"record": {"token_hash": "t5", "created_at": "2026-04-08T00:00:00Z", "sub": "citizen-5"}}),
        )
        runtime.dispatch(
            "POST",
            "/api/v1/offline-sync/flush",
            headers={"Authorization": "Bearer admin-operator-5"},
            body=json.dumps(
                {
                    "device_id": "device-1",
                    "remote_records": [{"token_hash": "t5", "created_at": "2026-04-08T00:01:00Z"}],
                    "approvers": ["official-1", "official-2"],
                }
            ),
        )
        status_code, payload = runtime.dispatch(
            "GET",
            "/api/v1/offline-sync/operations/export",
            headers={"Authorization": "Bearer admin-operator-5"},
        )
        self.assertEqual(status_code, 200)
        export_payload = payload["export"]["payload"]
        export = json.loads(export_payload)
        self.assertEqual(export["service"], "offline_sync_service")
        decision = export["operations"][0]["conflict_report"]["decisions"][0]
        self.assertNotIn("sub", decision)
        public_key_pem = runtime.device_public_keys["device-1"]
        self.assertTrue(
            Phase1CryptoProvider().verify_bytes(
                export_payload.encode("utf-8"),
                payload["export"]["signature"],
                public_key_pem,
            )
        )
        self.assertEqual(runtime.dependencies.audit_logger.entries()[-1].event_type, "offline_sync_operation_exported")

    def test_offline_sync_runtime_builds_evidence_bundle_for_operations(self) -> None:
        runtime = self.build_runtime()
        runtime.dispatch(
            "POST",
            "/api/v1/offline-sync/stage",
            headers={"Authorization": "Bearer admin-operator-6"},
            body=json.dumps({"record": {"token_hash": "t6", "created_at": "2026-04-08T00:00:00Z", "name": "Sensitive"}}),
        )
        runtime.dispatch(
            "POST",
            "/api/v1/offline-sync/flush",
            headers={"Authorization": "Bearer admin-operator-6"},
            body=json.dumps(
                {
                    "device_id": "device-1",
                    "remote_records": [{"token_hash": "t6", "created_at": "2026-04-08T00:01:00Z"}],
                    "approvers": ["official-1", "official-2"],
                }
            ),
        )
        status_code, payload = runtime.dispatch(
            "GET",
            "/api/v1/offline-sync/operations/evidence-bundle",
            headers={"Authorization": "Bearer admin-operator-6"},
            body=json.dumps({"case_id": "case-offline-6"}),
        )
        self.assertEqual(status_code, 200)
        bundle = payload["bundle"]
        self.assertEqual(bundle["case_id"], "case-offline-6")
        self.assertEqual(bundle["artifacts"][0]["kind"], "offline_sync_export")
        self.assertEqual(bundle["artifacts"][0]["metadata"]["artifact_role"], "offline_sync_reconciliation")
        self.assertEqual(bundle["custody_events"][0]["action"], "offline_sync_export_signed")
        self.assertEqual(bundle["custody_events"][1]["action"], "bundle_created")
        self.assertEqual(
            runtime.dependencies.audit_logger.entries()[-1].event_type,
            "offline_sync_evidence_bundle_generated",
        )

    def test_offline_sync_runtime_accepts_query_params_for_browser_get_routes(self) -> None:
        runtime = self.build_runtime()
        runtime.dispatch(
            "POST",
            "/api/v1/offline-sync/stage",
            headers={"Authorization": "Bearer admin-operator-query"},
            body=json.dumps({"record": {"token_hash": "tq1", "created_at": "2026-04-08T00:00:00Z"}}),
        )
        runtime.dispatch(
            "POST",
            "/api/v1/offline-sync/flush",
            headers={"Authorization": "Bearer admin-operator-query"},
            body=json.dumps(
                {
                    "device_id": "device-1",
                    "remote_records": [{"token_hash": "tq1", "created_at": "2026-04-08T00:01:00Z"}],
                    "approvers": ["official-1", "official-2"],
                }
            ),
        )
        status_code, export_payload = runtime.dispatch(
            "GET",
            "/api/v1/offline-sync/operations/export?device_id=device-1",
            headers={"Authorization": "Bearer admin-operator-query"},
        )
        self.assertEqual(status_code, 200)
        self.assertIn("signature", export_payload["export"])
        status_code, bundle_payload = runtime.dispatch(
            "GET",
            "/api/v1/offline-sync/operations/evidence-bundle?case_id=browser-case&device_id=device-1",
            headers={"Authorization": "Bearer admin-operator-query"},
        )
        self.assertEqual(status_code, 200)
        self.assertEqual(bundle_payload["bundle"]["case_id"], "browser-case")

    def test_offline_sync_runtime_status_reports_recent_activity(self) -> None:
        runtime = self.build_runtime()
        runtime.dispatch(
            "POST",
            "/api/v1/offline-sync/stage",
            headers={"Authorization": "Bearer admin-operator-3"},
            body=json.dumps({"record": {"token_hash": "t3", "created_at": "2026-04-08T00:00:00Z"}}),
        )
        runtime.dispatch(
            "GET",
            "/api/v1/offline-sync/queue",
            headers={"Authorization": "Bearer admin-operator-3"},
        )
        status_code, payload = runtime.dispatch(
            "GET",
            "/api/v1/offline-sync/status",
            headers={"Authorization": "Bearer admin-operator-3"},
        )
        self.assertEqual(status_code, 200)
        self.assertEqual(payload["report"]["queue_depth"], 1)
        self.assertEqual(payload["report"]["approval_history_count"], 0)
        self.assertEqual(payload["report"]["operation_history_count"], 0)
        self.assertEqual(payload["report"]["offline_sync_conflict_total"], 0)
        self.assertEqual(payload["report"]["latest_audit_event"], "offline_sync_queue_inspected")
        self.assertIsNone(payload["report"]["latest_evidence_event"])
        self.assertIn("approval_store", payload["report"])
        self.assertIn("operation_store", payload["report"])

    def test_offline_sync_runtime_status_reports_evidence_posture(self) -> None:
        runtime = self.build_runtime()
        runtime.dispatch(
            "POST",
            "/api/v1/offline-sync/stage",
            headers={"Authorization": "Bearer admin-operator-7"},
            body=json.dumps({"record": {"token_hash": "t7", "created_at": "2026-04-08T00:00:00Z"}}),
        )
        runtime.dispatch(
            "POST",
            "/api/v1/offline-sync/flush",
            headers={"Authorization": "Bearer admin-operator-7"},
            body=json.dumps(
                {
                    "device_id": "device-1",
                    "remote_records": [{"token_hash": "t7", "created_at": "2026-04-08T00:01:00Z"}],
                    "approvers": ["official-1", "official-2"],
                }
            ),
        )
        runtime.dispatch(
            "GET",
            "/api/v1/offline-sync/operations/evidence-bundle",
            headers={"Authorization": "Bearer admin-operator-7"},
            body=json.dumps({"case_id": "case-offline-7"}),
        )
        status_code, payload = runtime.dispatch(
            "GET",
            "/api/v1/offline-sync/status",
            headers={"Authorization": "Bearer admin-operator-7"},
        )
        self.assertEqual(status_code, 200)
        self.assertEqual(payload["report"]["operation_history_count"], 1)
        self.assertEqual(payload["report"]["offline_sync_conflict_total"], 1)
        self.assertEqual(payload["report"]["latest_evidence_event"], "offline_sync_evidence_bundle_generated")

    def test_offline_sync_runtime_rejects_non_admin_token(self) -> None:
        runtime = self.build_runtime()
        with self.assertRaises(PermissionError):
            runtime.dispatch("GET", "/api/v1/offline-sync/queue", headers={"Authorization": "Bearer demo-user"})
        self.assertEqual(runtime.dependencies.audit_logger.entries()[-1].event_type, "offline_sync_auth_rejected")
        self.assertEqual(
            runtime.dependencies.audit_logger.entries()[-1].payload["reason"],
            "missing_admin_bearer_token",
        )

    def test_offline_sync_runtime_rejects_admin_token_with_invalid_operator_id(self) -> None:
        runtime = self.build_runtime()
        with self.assertRaises(PermissionError):
            runtime.dispatch(
                "GET",
                "/api/v1/offline-sync/queue",
                headers={"Authorization": "Bearer admin-OPERATOR!"},
            )
        self.assertEqual(runtime.dependencies.audit_logger.entries()[-1].event_type, "offline_sync_auth_rejected")
        self.assertEqual(
            runtime.dependencies.audit_logger.entries()[-1].payload["reason"],
            "invalid_admin_operator_id",
        )

    def test_offline_sync_runtime_rejects_unknown_device_id_for_flush(self) -> None:
        runtime = self.build_runtime()
        runtime.dispatch(
            "POST",
            "/api/v1/offline-sync/stage",
            headers={"Authorization": "Bearer admin-operator-unknown-device"},
            body=json.dumps({"record": {"token_hash": "tx1", "created_at": "2026-04-08T00:00:00Z"}}),
        )
        with self.assertRaises(ValueError):
            runtime.dispatch(
                "POST",
                "/api/v1/offline-sync/flush",
                headers={"Authorization": "Bearer admin-operator-unknown-device"},
                body=json.dumps(
                    {
                        "device_id": "device-does-not-exist",
                        "remote_records": [{"token_hash": "tx1", "created_at": "2026-04-08T00:01:00Z"}],
                        "approvers": ["official-1", "official-2"],
                    }
                ),
            )
        self.assertEqual(runtime.dependencies.audit_logger.entries()[-1].event_type, "offline_sync_device_rejected")
        self.assertEqual(
            runtime.dependencies.audit_logger.entries()[-1].payload["reason"],
            "unknown_device_id",
        )


if __name__ == "__main__":
    unittest.main()
