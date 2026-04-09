from __future__ import annotations

import json
import unittest

from services.api_gateway.local_runtime import LocalGatewayRuntime
from services.voting_service.services.verification_gateway import VerificationGateway


class PIIStubClient:
    def validate_token(self, token: str) -> dict[str, object]:
        return {
            "jti": "token-identity-boundary",
            "exp": 9999999999,
            "iat": 1111111111,
            "iss": "external-nid",
            "aud": "securevote-png",
            "name": "Sensitive Name",
            "address": "Sensitive Address",
            "sub": "citizen-record-22",
            "eligible": True,
            "biometrics": {"face": "template"},
        }

    def check_eligibility(self, token: str) -> bool:
        return True


class LocalRuntimeTests(unittest.TestCase):
    def test_health_endpoint_returns_ok(self) -> None:
        runtime = LocalGatewayRuntime.build()
        status_code, payload = runtime.dispatch("GET", "/health", headers={})
        self.assertEqual(status_code, 200)
        self.assertEqual(payload["status"], "ok")

    def test_verify_token_endpoint_accepts_demo_token(self) -> None:
        runtime = LocalGatewayRuntime.build()
        status_code, payload = runtime.dispatch(
            "POST",
            "/api/v1/vote/verify-token",
            headers={"Authorization": "Bearer demo-voter-1"},
            body=json.dumps({"token": "demo-voter-1"}),
        )
        self.assertEqual(status_code, 200)
        self.assertEqual(payload["claims"]["jti"], "voter-1")

    def test_verify_token_endpoint_strips_identity_claims(self) -> None:
        runtime = LocalGatewayRuntime.build()
        runtime.verification_gateway = VerificationGateway(client=PIIStubClient())  # type: ignore[arg-type]
        status_code, payload = runtime.dispatch(
            "POST",
            "/api/v1/vote/verify-token",
            headers={"Authorization": "Bearer demo-voter-identity"},
            body=json.dumps({"token": "demo-voter-identity"}),
        )
        self.assertEqual(status_code, 200)
        self.assertEqual(
            payload["claims"],
            {
                "jti": "token-identity-boundary",
                "exp": 9999999999,
                "iat": 1111111111,
                "iss": "external-nid",
                "aud": "securevote-png",
            },
        )

    def test_nid_verify_endpoint_strips_identity_claims(self) -> None:
        runtime = LocalGatewayRuntime.build()
        runtime.verification_gateway = VerificationGateway(client=PIIStubClient())  # type: ignore[arg-type]
        status_code, payload = runtime.dispatch(
            "POST",
            "/api/v1/nid/verify",
            headers={},
            body=json.dumps({"token": "demo-voter-identity"}),
        )
        self.assertEqual(status_code, 200)
        self.assertEqual(
            payload["claims"],
            {
                "jti": "token-identity-boundary",
                "exp": 9999999999,
                "iat": 1111111111,
                "iss": "external-nid",
                "aud": "securevote-png",
            },
        )

    def test_cast_vote_endpoint_returns_encrypted_vote(self) -> None:
        runtime = LocalGatewayRuntime.build()
        status_code, payload = runtime.dispatch(
            "POST",
            "/api/v1/vote/cast",
            headers={"Authorization": "Bearer demo-voter-2", "X-Device-ID": "device-1"},
            body=json.dumps(
                {
                    "token": "demo-voter-2",
                    "ballot_id": "ballot-2026",
                    "election_id": "election-2026",
                    "device_id": "device-1",
                    "selections": {"president": "candidate-a"},
                }
            ),
        )
        self.assertEqual(status_code, 201)
        self.assertIn("encrypted_vote", payload["vote"])
        self.assertIn("token_hash", payload["vote"])

    def test_observer_audit_endpoint_returns_hash_chained_entries(self) -> None:
        runtime = LocalGatewayRuntime.build()
        runtime.dispatch(
            "POST",
            "/api/v1/vote/cast",
            headers={"Authorization": "Bearer demo-voter-3", "X-Device-ID": "device-1"},
            body=json.dumps(
                {
                    "token": "demo-voter-3",
                    "ballot_id": "ballot-2026",
                    "election_id": "election-2026",
                    "device_id": "device-1",
                    "selections": {"president": "candidate-b"},
                }
            ),
        )

        status_code, payload = runtime.dispatch(
            "GET",
            "/api/v1/vote/observer/audit",
            headers={"Authorization": "Bearer observer-auditor-1"},
        )
        self.assertEqual(status_code, 200)
        self.assertTrue(payload["audit_log_valid"])
        self.assertEqual(payload["entries"][-1]["event_type"], "vote_cast")

    def test_observer_audit_endpoint_redacts_sensitive_payload_fields(self) -> None:
        runtime = LocalGatewayRuntime.build()
        runtime.dependencies.audit_logger.append(
            "bad_upstream_event",
            {
                "name": "Sensitive Name",
                "sub": "citizen-7",
                "token": "raw-token",
                "nested": {"address": "Sensitive Address"},
                "election_id": "election-2026",
            },
        )
        status_code, payload = runtime.dispatch(
            "GET",
            "/api/v1/vote/observer/audit",
            headers={"Authorization": "Bearer observer-auditor-1"},
        )
        self.assertEqual(status_code, 200)
        entry_payload = payload["entries"][-1]["payload"]
        self.assertEqual(entry_payload["name"], "[redacted]")
        self.assertEqual(entry_payload["sub"], "[redacted]")
        self.assertEqual(entry_payload["token"], "[redacted]")
        self.assertEqual(entry_payload["nested"]["address"], "[redacted]")
        self.assertEqual(entry_payload["election_id"], "election-2026")

    def test_observer_audit_export_redacts_sensitive_payload_fields(self) -> None:
        runtime = LocalGatewayRuntime.build()
        runtime.dependencies.audit_logger.append(
            "bad_export_event",
            {"biometrics": {"face": "template"}, "authorization": "Bearer secret", "election_id": "election-2026"},
        )
        status_code, payload = runtime.dispatch(
            "GET",
            "/api/v1/vote/observer/audit/export",
            headers={"Authorization": "Bearer observer-auditor-1"},
        )
        self.assertEqual(status_code, 200)
        entry_payload = payload["audit_log"][-1]["payload"]
        self.assertEqual(entry_payload["biometrics"], "[redacted]")
        self.assertEqual(entry_payload["authorization"], "[redacted]")
        self.assertEqual(entry_payload["election_id"], "election-2026")

    def test_observer_audit_endpoint_rejects_non_observer_token(self) -> None:
        runtime = LocalGatewayRuntime.build()
        with self.assertRaises(PermissionError):
            runtime.dispatch(
                "GET",
                "/api/v1/vote/observer/audit",
                headers={"Authorization": "Bearer demo-voter-4"},
            )

    def test_observer_tally_endpoint_returns_decrypted_totals(self) -> None:
        runtime = LocalGatewayRuntime.build()
        runtime.dispatch(
            "POST",
            "/api/v1/vote/cast",
            headers={"Authorization": "Bearer demo-voter-5", "X-Device-ID": "device-1"},
            body=json.dumps(
                {
                    "token": "demo-voter-5",
                    "ballot_id": "ballot-2026",
                    "election_id": "election-2026",
                    "device_id": "device-1",
                    "selections": {"president": "candidate-a"},
                }
            ),
        )

        status_code, payload = runtime.dispatch(
            "GET",
            "/api/v1/vote/observer/tally/election-2026",
            headers={"Authorization": "Bearer observer-auditor-2"},
        )
        self.assertEqual(status_code, 200)
        self.assertEqual(payload["tally"]["candidate-a"], 1)

    def test_paper_reconciliation_endpoint_returns_zero_delta_for_matching_counts(self) -> None:
        runtime = LocalGatewayRuntime.build()
        runtime.dispatch(
            "POST",
            "/api/v1/vote/cast",
            headers={"Authorization": "Bearer demo-voter-6", "X-Device-ID": "device-1"},
            body=json.dumps(
                {
                    "token": "demo-voter-6",
                    "ballot_id": "ballot-2026",
                    "election_id": "election-2026",
                    "device_id": "device-1",
                    "selections": {"president": "candidate-b"},
                }
            ),
        )

        status_code, payload = runtime.dispatch(
            "POST",
            "/api/v1/vote/observer/paper-reconcile",
            headers={"Authorization": "Bearer observer-auditor-3"},
            body=json.dumps(
                {
                    "election_id": "election-2026",
                    "paper_ballots": ["candidate-b"],
                }
            ),
        )
        self.assertEqual(status_code, 200)
        self.assertEqual(payload["delta"]["candidate-b"], 0)

    def test_compliance_report_endpoint_reflects_audit_chain(self) -> None:
        runtime = LocalGatewayRuntime.build()
        runtime.dispatch(
            "POST",
            "/api/v1/vote/cast",
            headers={"Authorization": "Bearer demo-voter-7", "X-Device-ID": "device-1"},
            body=json.dumps(
                {
                    "token": "demo-voter-7",
                    "ballot_id": "ballot-2026",
                    "election_id": "election-2026",
                    "device_id": "device-1",
                    "selections": {"president": "candidate-c"},
                }
            ),
        )

        status_code, payload = runtime.dispatch(
            "GET",
            "/api/v1/vote/compliance/report",
            headers={"Authorization": "Bearer observer-auditor-4"},
        )
        self.assertEqual(status_code, 200)
        self.assertTrue(payload["report"]["hash_chain_valid"])
        self.assertEqual(payload["report"]["latest_event"], "vote_cast")
        self.assertEqual(payload["report"]["offline_sync_operation_count"], 0)
        self.assertIsNone(payload["report"]["latest_evidence_event"])

    def test_compliance_report_endpoint_includes_offline_sync_posture(self) -> None:
        runtime = LocalGatewayRuntime.build()
        runtime.dispatch(
            "POST",
            "/api/v1/vote/admin/offline-sync/stage",
            headers={"Authorization": "Bearer admin-operator-10"},
            body=json.dumps(
                {
                    "record": {
                        "token_hash": "t10",
                        "created_at": "2026-04-08T00:00:00Z",
                    }
                }
            ),
        )
        runtime.dispatch(
            "POST",
            "/api/v1/vote/admin/offline-sync/flush",
            headers={"Authorization": "Bearer admin-operator-10"},
            body=json.dumps(
                {
                    "device_id": "device-1",
                    "remote_records": [
                        {
                            "token_hash": "t10",
                            "created_at": "2026-04-08T00:01:00Z",
                        }
                    ],
                    "approvers": ["official-1", "official-2"],
                }
            ),
        )
        runtime.dispatch(
            "GET",
            "/api/v1/vote/compliance/offline-sync-evidence",
            headers={"Authorization": "Bearer observer-auditor-10"},
            body=json.dumps({"case_id": "case-offline-10"}),
        )
        status_code, payload = runtime.dispatch(
            "GET",
            "/api/v1/vote/compliance/report",
            headers={"Authorization": "Bearer observer-auditor-10"},
        )
        self.assertEqual(status_code, 200)
        self.assertEqual(payload["report"]["offline_sync_operation_count"], 1)
        self.assertEqual(payload["report"]["offline_sync_conflict_total"], 1)
        self.assertIsNotNone(payload["report"]["latest_offline_sync_operation_id"])
        self.assertEqual(payload["report"]["latest_evidence_event"], "offline_sync_evidence_bundle_generated")

    def test_compliance_offline_sync_evidence_endpoint_returns_bundle(self) -> None:
        runtime = LocalGatewayRuntime.build()
        runtime.dispatch(
            "POST",
            "/api/v1/vote/admin/offline-sync/stage",
            headers={"Authorization": "Bearer admin-operator-8"},
            body=json.dumps(
                {
                    "record": {
                        "token_hash": "t5",
                        "created_at": "2026-04-08T00:00:00Z",
                        "sub": "citizen-5",
                    }
                }
            ),
        )
        runtime.dispatch(
            "POST",
            "/api/v1/vote/admin/offline-sync/flush",
            headers={"Authorization": "Bearer admin-operator-8"},
            body=json.dumps(
                {
                    "device_id": "device-1",
                    "remote_records": [
                        {
                            "token_hash": "t5",
                            "created_at": "2026-04-08T00:01:00Z",
                        }
                    ],
                    "approvers": ["official-1", "official-2"],
                }
            ),
        )
        status_code, payload = runtime.dispatch(
            "GET",
            "/api/v1/vote/compliance/offline-sync-evidence",
            headers={"Authorization": "Bearer observer-auditor-5"},
            body=json.dumps({"case_id": "case-offline-5"}),
        )
        self.assertEqual(status_code, 200)
        self.assertEqual(payload["bundle"]["case_id"], "case-offline-5")
        self.assertEqual(payload["bundle"]["artifacts"][0]["kind"], "offline_sync_export")
        self.assertEqual(
            payload["bundle"]["artifacts"][0]["operations"][0]["conflict_report"]["decisions"][0]["token_hash"],
            "t5",
        )
        self.assertEqual(
            payload["bundle"]["artifacts"][0]["operations"][0]["conflict_report"]["decisions"][0].get("sub"),
            None,
        )
        self.assertEqual(
            runtime.dependencies.audit_logger.entries()[-1].event_type,
            "offline_sync_evidence_bundle_generated",
        )

    def test_compliance_offline_sync_evidence_endpoint_accepts_query_params(self) -> None:
        runtime = LocalGatewayRuntime.build()
        runtime.dispatch(
            "POST",
            "/api/v1/vote/admin/offline-sync/stage",
            headers={"Authorization": "Bearer admin-operator-11"},
            body=json.dumps(
                {
                    "record": {
                        "token_hash": "t11",
                        "created_at": "2026-04-08T00:00:00Z",
                    }
                }
            ),
        )
        runtime.dispatch(
            "POST",
            "/api/v1/vote/admin/offline-sync/flush",
            headers={"Authorization": "Bearer admin-operator-11"},
            body=json.dumps(
                {
                    "device_id": "device-1",
                    "remote_records": [
                        {
                            "token_hash": "t11",
                            "created_at": "2026-04-08T00:01:00Z",
                        }
                    ],
                    "approvers": ["official-1", "official-2"],
                }
            ),
        )
        status_code, payload = runtime.dispatch(
            "GET",
            "/api/v1/vote/compliance/offline-sync-evidence?case_id=query-case&device_id=device-1",
            headers={"Authorization": "Bearer observer-auditor-11"},
        )
        self.assertEqual(status_code, 200)
        self.assertEqual(payload["bundle"]["case_id"], "query-case")

    def test_compliance_offline_sync_evidence_endpoint_rejects_non_observer_token(self) -> None:
        runtime = LocalGatewayRuntime.build()
        with self.assertRaises(PermissionError):
            runtime.dispatch(
                "GET",
                "/api/v1/vote/compliance/offline-sync-evidence",
                headers={"Authorization": "Bearer demo-voter-9"},
            )

    def test_admin_phase_transition_endpoint_updates_runtime_state(self) -> None:
        runtime = LocalGatewayRuntime.build()
        status_code, payload = runtime.dispatch(
            "POST",
            "/api/v1/vote/admin/phase-transition",
            headers={"Authorization": "Bearer admin-operator-1"},
            body=json.dumps(
                {
                    "election_id": "election-2026",
                    "next_phase": "locked",
                    "approvers": ["official-1", "official-2"],
                }
            ),
        )
        self.assertEqual(status_code, 200)
        self.assertEqual(payload["state"]["phase"], "locked")

    def test_admin_freeze_endpoint_blocks_vote_casting(self) -> None:
        runtime = LocalGatewayRuntime.build()
        runtime.dispatch(
            "POST",
            "/api/v1/vote/admin/freeze/activate",
            headers={"Authorization": "Bearer admin-operator-2"},
            body=json.dumps(
                {
                    "election_id": "election-2026",
                    "reason": "security-incident",
                    "approvers": ["official-1", "official-2", "official-3"],
                }
            ),
        )

        with self.assertRaises(ValueError):
            runtime.dispatch(
                "POST",
                "/api/v1/vote/cast",
                headers={"Authorization": "Bearer demo-voter-8", "X-Device-ID": "device-1"},
                body=json.dumps(
                    {
                        "token": "demo-voter-8",
                        "ballot_id": "ballot-2026",
                        "election_id": "election-2026",
                        "device_id": "device-1",
                        "selections": {"president": "candidate-a"},
                    }
                ),
            )

    def test_admin_state_endpoint_returns_phase_history(self) -> None:
        runtime = LocalGatewayRuntime.build()
        runtime.dispatch(
            "POST",
            "/api/v1/vote/admin/phase-transition",
            headers={"Authorization": "Bearer admin-operator-3"},
            body=json.dumps(
                {
                    "election_id": "election-2026",
                    "next_phase": "locked",
                    "approvers": ["official-1", "official-2"],
                }
            ),
        )
        status_code, payload = runtime.dispatch(
            "GET",
            "/api/v1/vote/admin/state/election-2026",
            headers={"Authorization": "Bearer admin-operator-3"},
        )
        self.assertEqual(status_code, 200)
        self.assertEqual(payload["state"]["phase"], "locked")
        self.assertEqual(payload["phase_history"][-1]["next_phase"], "locked")

    def test_admin_offline_sync_queue_endpoint_returns_staged_records(self) -> None:
        runtime = LocalGatewayRuntime.build()
        runtime.dispatch(
            "POST",
            "/api/v1/vote/admin/offline-sync/stage",
            headers={"Authorization": "Bearer admin-operator-4"},
            body=json.dumps(
                {
                    "record": {
                        "token_hash": "t1",
                        "created_at": "2026-04-07T00:00:00Z",
                        "sub": "citizen-1",
                    }
                }
            ),
        )
        status_code, payload = runtime.dispatch(
            "GET",
            "/api/v1/vote/admin/offline-sync/queue",
            headers={"Authorization": "Bearer admin-operator-4"},
        )
        self.assertEqual(status_code, 200)
        self.assertEqual(payload["queue_depth"], 1)
        self.assertEqual(payload["queued_records"][0]["sub"], "[redacted]")
        self.assertEqual(runtime.dependencies.audit_logger.entries()[-2].event_type, "offline_sync_record_staged")
        self.assertEqual(runtime.dependencies.audit_logger.entries()[-1].event_type, "offline_sync_queue_inspected")

    def test_admin_offline_sync_flush_returns_signed_artifacts(self) -> None:
        runtime = LocalGatewayRuntime.build()
        runtime.dispatch(
            "POST",
            "/api/v1/vote/admin/offline-sync/stage",
            headers={"Authorization": "Bearer admin-operator-5"},
            body=json.dumps(
                {
                    "record": {
                        "token_hash": "t2",
                        "created_at": "2026-04-07T00:00:00Z",
                        "vote": "local",
                    }
                }
            ),
        )
        status_code, payload = runtime.dispatch(
            "POST",
            "/api/v1/vote/admin/offline-sync/flush",
            headers={"Authorization": "Bearer admin-operator-5"},
            body=json.dumps(
                {
                    "device_id": "device-1",
                    "remote_records": [
                        {
                            "token_hash": "t2",
                            "created_at": "2026-04-07T00:01:00Z",
                            "vote": "remote",
                        }
                    ],
                    "approvers": ["official-1", "official-2"],
                }
            ),
        )
        self.assertEqual(status_code, 200)
        self.assertEqual(payload["queue_depth"], 0)
        self.assertTrue(payload["manifest_valid"])
        self.assertEqual(payload["artifacts"]["manifest"]["device_id"], "device-1")
        self.assertEqual(payload["artifacts"]["conflict_report"]["conflict_count"], 1)
        self.assertEqual(runtime.dependencies.audit_logger.entries()[-1].event_type, "offline_sync_flushed")
        self.assertEqual(runtime.dependencies.audit_logger.entries()[-1].payload["operator_id"], "operator-5")

    def test_admin_offline_sync_flush_rejects_conflicts_without_two_approvers(self) -> None:
        runtime = LocalGatewayRuntime.build()
        runtime.dispatch(
            "POST",
            "/api/v1/vote/admin/offline-sync/stage",
            headers={"Authorization": "Bearer admin-operator-6"},
            body=json.dumps(
                {
                    "record": {
                        "token_hash": "t3",
                        "created_at": "2026-04-07T00:00:00Z",
                        "vote": "local",
                    }
                }
            ),
        )
        with self.assertRaises(ValueError):
            runtime.dispatch(
                "POST",
                "/api/v1/vote/admin/offline-sync/flush",
                headers={"Authorization": "Bearer admin-operator-6"},
                body=json.dumps(
                    {
                        "device_id": "device-1",
                        "remote_records": [
                            {
                                "token_hash": "t3",
                                "created_at": "2026-04-07T00:01:00Z",
                                "vote": "remote",
                            }
                        ],
                        "approvers": ["official-1"],
                    }
                ),
            )
        self.assertEqual(runtime.dependencies.audit_logger.entries()[-1].event_type, "offline_sync_flush_rejected")
        self.assertEqual(runtime.dependencies.audit_logger.entries()[-1].payload["required_approvals"], 2)

    def test_admin_offline_sync_approvals_endpoint_returns_history(self) -> None:
        runtime = LocalGatewayRuntime.build()
        runtime.dispatch(
            "POST",
            "/api/v1/vote/admin/offline-sync/stage",
            headers={"Authorization": "Bearer admin-operator-7"},
            body=json.dumps(
                {
                    "record": {
                        "token_hash": "t4",
                        "created_at": "2026-04-08T00:00:00Z",
                    }
                }
            ),
        )
        flush_status, flush_payload = runtime.dispatch(
            "POST",
            "/api/v1/vote/admin/offline-sync/flush",
            headers={"Authorization": "Bearer admin-operator-7"},
            body=json.dumps(
                {
                    "device_id": "device-1",
                    "remote_records": [
                        {
                            "token_hash": "t4",
                            "created_at": "2026-04-08T00:01:00Z",
                        }
                    ],
                    "approvers": ["official-1", "official-2"],
                }
            ),
        )
        self.assertEqual(flush_status, 200)
        operation_id = runtime.dependencies.audit_logger.entries()[-1].payload["operation_id"]
        status_code, payload = runtime.dispatch(
            "GET",
            "/api/v1/vote/admin/offline-sync/approvals",
            headers={"Authorization": "Bearer admin-operator-7"},
            body=json.dumps({"operation_id": operation_id}),
        )
        self.assertEqual(status_code, 200)
        self.assertEqual(len(payload["approvals"]), 2)
        self.assertEqual(payload["approvals"][0]["operation_id"], operation_id)


if __name__ == "__main__":
    unittest.main()
