"""Local demo runtime for the SecureVote PNG gateway and voting service."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass, replace
from datetime import datetime, timedelta, timezone
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qsl, urlparse

from election_state.control_plane import ElectionControlPlane, ElectionControlSnapshot
from human_factors.multi_person_auth.approval_tracking import ApprovalTracker
from legal_evidence import generate_offline_sync_evidence_bundle
from services.api_gateway.app import GatewayApplication
from services.api_gateway.auth_proxy import AuthProxy
from services.api_gateway.routing import GatewayRouter
from services.audit_service import WORMLogger
from services.audit_service.detection.tamper import verify_hash_chain
from services.audit_service.observer.export_audit import export_audit_log
from services.audit_service.observer.read_only_api import fetch_audit_entries
from services.audit_service.reports.compliance import generate_compliance_report
from services.endpoint_inventory import LOCAL_RUNTIME_ENDPOINTS, render_inventory_lines
from services.nid_client.exceptions import NIDValidationError
from services.offline_sync_service.api.operator import OfflineSyncOperatorAPI
from services.offline_sync_service.factory import build_offline_sync_dependencies
from paper_trail.manual_recount import recount_ballots
from paper_trail.paper_vs_digital_reconcile import reconcile
from services.offline_sync_service.sync.engine import SyncEngine
from services.voting_service.api.v1.cast_vote import cast_vote
from services.voting_service.api.v1.get_ballot import get_ballot
from services.voting_service.api.v1.observer_tally import observer_tally
from services.voting_service.api.v1.public_result import public_result
from services.voting_service.api.v1.verify_token import verify_token
from services.voting_service.factory import build_voting_dependencies
from services.voting_service.models.election_state import ElectionState
from services.voting_service.services.ballot_service import BallotService
from services.voting_service.services.election_state_manager import ElectionStateManager
from services.voting_service.services.result_hash_publisher import ResultHashPublisher
from services.voting_service.services.token_consumer import TokenConsumer
from services.voting_service.services.token_replay_detector import TokenReplayDetector
from services.voting_service.services.verification_gateway import VerificationGateway
from services.voting_service.crypto.phase1_standard import Phase1StandardCrypto
from services.voting_service.services.tally_service import TallyService
from services.voting_service.services.vote_repository import VoteRepository


class DemoTokenValidator:
    """Local-only validator used when an external NID service is unavailable."""

    def validate(self, token: str) -> dict[str, object]:
        if not isinstance(token, str) or not (token.startswith("demo-") or token.startswith("observer-") or token.startswith("admin-")):
            raise NIDValidationError("Local demo requires tokens starting with demo-, observer-, or admin-")
        now = datetime.now(timezone.utc)
        return {
            "jti": token.removeprefix("demo-"),
            "iss": "securevote-local-demo",
            "aud": "securevote-png",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=5)).timestamp()),
        }


class DemoNIDClient:
    """Deterministic local NID stub for development and smoke testing."""

    def __init__(self, token_validator: DemoTokenValidator | None = None) -> None:
        self.token_validator = token_validator or DemoTokenValidator()

    def validate_token(self, token: str) -> dict[str, object]:
        return self.token_validator.validate(token)

    def check_eligibility(self, token: str) -> bool:
        return not token.endswith("-blocked")


@dataclass
class LocalGatewayRuntime:
    """In-process HTTP runtime that exercises the gateway and voting flow."""

    app: GatewayApplication
    verification_gateway: VerificationGateway
    dependencies: Any
    control_plane: ElectionControlPlane
    offline_sync_engine: SyncEngine
    offline_sync_api: OfflineSyncOperatorAPI
    tally_public_key_pem: str
    tally_private_key_pem: str
    device_private_keys: dict[str, str]
    device_public_keys: dict[str, str]

    @classmethod
    def build(cls) -> LocalGatewayRuntime:
        token_validator = DemoTokenValidator()
        app = GatewayApplication(
            router=GatewayRouter(),
            auth_proxy=AuthProxy(token_validator=token_validator),
        )
        verification_gateway = VerificationGateway(client=DemoNIDClient())  # type: ignore[arg-type]
        demo_election_state = ElectionState("election-2026", "voting", False)
        demo_audit_logger = WORMLogger()
        base_dependencies = replace(build_voting_dependencies(), audit_logger=demo_audit_logger)
        dependencies = replace(
            base_dependencies,
            election_state_manager=ElectionStateManager(demo_election_state),
            token_consumer=TokenConsumer(),
            replay_detector=TokenReplayDetector(),
            result_hash_publisher=ResultHashPublisher(),
            vote_repository=VoteRepository(),
            control_plane=ElectionControlPlane(
                initial_state=ElectionControlSnapshot(
                    election_id=demo_election_state.election_id,
                    phase=demo_election_state.phase,
                    freeze_active=demo_election_state.freeze_active,
                    freeze_reason="",
                ),
                audit_logger=demo_audit_logger,
            ),
        )
        crypto = Phase1StandardCrypto()
        tally_private_key = crypto.generate_rsa_private_key()
        tally_private_key_pem = crypto.serialize_private_key(tally_private_key)
        tally_public_key_pem = crypto.serialize_public_key(tally_private_key.public_key())
        device_keypair = crypto.generate_rsa_private_key()
        device_private_key = crypto.serialize_private_key(device_keypair)
        device_public_key = crypto.serialize_public_key(device_keypair.public_key())
        offline_sync_dependencies = build_offline_sync_dependencies(
            audit_logger=demo_audit_logger,
            force_in_memory=True,
        )
        dependencies.result_hash_publisher.publish(
            "election-2026",
            {"candidate-a": 0, "candidate-b": 0, "candidate-c": 0},
        )
        return cls(
            app=app,
            verification_gateway=verification_gateway,
            dependencies=dependencies,
            control_plane=dependencies.control_plane,
            offline_sync_engine=offline_sync_dependencies.engine,
            offline_sync_api=offline_sync_dependencies.operator_api,
            tally_public_key_pem=tally_public_key_pem,
            tally_private_key_pem=tally_private_key_pem,
            device_private_keys={"device-1": device_private_key},
            device_public_keys={"device-1": device_public_key},
        )

    def _demo_certificate(self, path: str) -> dict[str, object]:
        if path.startswith("/api/v1/nid/"):
            return {
                "subject": "CN=nid-client.internal,O=SecureVote PNG,C=PG",
                "spiffe_id": "spiffe://securevote/internal/nid-client",
                "chain_verified": True,
                "client_auth": True,
                "not_before": "2026-01-01T00:00:00+00:00",
                "not_after": "2027-01-01T00:00:00+00:00",
            }
        return {
            "subject": "CN=voting-service.internal,O=SecureVote PNG,C=PG",
            "spiffe_id": "spiffe://securevote/internal/voting-service",
            "chain_verified": True,
            "client_auth": True,
            "not_before": "2026-01-01T00:00:00+00:00",
            "not_after": "2027-01-01T00:00:00+00:00",
        }

    def _build_gateway_request(
        self,
        *,
        method: str,
        path: str,
        query: dict[str, str],
        headers: dict[str, str],
        body: str,
    ) -> dict[str, object]:
        return {
            "method": method,
            "path": path,
            "query": query,
            "headers": headers,
            "body": body,
            # Local demo runtime is loopback-only and synthesizes transport metadata.
            "is_tls": True,
            "ip": "127.0.0.1",
            "client_certificate_verified": True,
            "client_certificate": self._demo_certificate(path),
        }

    def _json_safe(self, value: object) -> object:
        if isinstance(value, datetime):
            return value.isoformat()
        if is_dataclass(value):
            return {key: self._json_safe(item) for key, item in asdict(value).items()}
        if isinstance(value, dict):
            return {str(key): self._json_safe(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [self._json_safe(item) for item in value]
        return value

    def _parse_body(self, body: str) -> dict[str, object]:
        if not body:
            return {}
        parsed = json.loads(body)
        if not isinstance(parsed, dict):
            raise ValueError("JSON request body must be an object")
        return parsed

    def _bearer_token(self, headers: dict[str, str]) -> str:
        authorization = headers.get("Authorization", "")
        scheme, _, token = authorization.partition(" ")
        if scheme != "Bearer" or not token:
            raise PermissionError("Authorization header must use Bearer token format")
        return token

    def _admin_token(self, headers: dict[str, str]) -> str:
        token = self._bearer_token(headers)
        if not token.startswith("admin-"):
            raise PermissionError("Administrator token is required")
        return token

    def _observer_token(self, headers: dict[str, str]) -> str:
        token = self._bearer_token(headers)
        if not token.startswith("observer-"):
            raise PermissionError("Observer token is required")
        return token

    def dispatch(self, method: str, path: str, headers: dict[str, str], body: str = "") -> tuple[int, dict[str, object]]:
        parsed = urlparse(path)
        if parsed.path == "/health":
            return 200, {"status": "ok", "service": "securevote_png", "phase": "phase1"}

        request = self._build_gateway_request(
            method=method,
            path=parsed.path,
            query=dict(parse_qsl(parsed.query, keep_blank_values=True)),
            headers=headers,
            body=body,
        )
        gateway_result = self.app.handle_request(request)
        normalized_path = str(gateway_result["request"]["path"])
        payload = self._parse_body(str(gateway_result["request"].get("body", "")))

        if normalized_path == "/api/v1/nid/verify":
            token = str(payload.get("token") or gateway_result["request"].get("query", {}).get("token", ""))
            claims = self.verification_gateway.validate_voting_token(token)
            return 200, {"route": "external_nid", "claims": self._json_safe(claims)}

        if normalized_path == "/api/v1/vote/verify-token":
            token = str(payload.get("token", ""))
            claims = verify_token(token, gateway=self.verification_gateway)
            return 200, {"route": "voting_service", "claims": self._json_safe(claims)}

        if normalized_path.startswith("/api/v1/vote/ballots/"):
            ballot_id = normalized_path.rsplit("/", 1)[-1]
            ballot = get_ballot(ballot_id, ballot_service=self.dependencies.ballot_service)
            return 200, {"route": "voting_service", "ballot": self._json_safe(ballot)}

        if normalized_path.startswith("/api/v1/vote/public-result/"):
            election_id = normalized_path.rsplit("/", 1)[-1]
            publication = self.dependencies.result_hash_publisher.get_publication(election_id)
            if publication is None:
                raise ValueError("Result publication not found")
            return 200, {"route": "voting_service", "publication": self._json_safe(public_result(publication))}

        if normalized_path.startswith("/api/v1/vote/admin/state/"):
            admin_token = self._admin_token(gateway_result["request"]["headers"])
            election_id = normalized_path.rsplit("/", 1)[-1]
            state = self.control_plane.get_state(election_id)
            history = self.control_plane.phase_history(election_id)
            return 200, {
                "route": "voting_service",
                "admin_token": admin_token.removeprefix("admin-"),
                "state": self._json_safe(state),
                "phase_history": self._json_safe(history),
            }

        if normalized_path == "/api/v1/vote/admin/phase-transition":
            admin_token = self._admin_token(gateway_result["request"]["headers"])
            election_id = str(payload.get("election_id", "election-2026"))
            next_phase = str(payload.get("next_phase", ""))
            approvers = tuple(str(value) for value in payload.get("approvers", ()))
            record = self.control_plane.transition_phase(election_id, next_phase, approvers)
            state = self.control_plane.get_state(election_id)
            self.dependencies.election_state_manager.set_state(
                ElectionState(election_id=election_id, phase=state.phase, freeze_active=state.freeze_active)
            )
            return 200, {
                "route": "voting_service",
                "admin_token": admin_token.removeprefix("admin-"),
                "state": self._json_safe(state),
                "phase_change": self._json_safe(record),
            }

        if normalized_path == "/api/v1/vote/admin/freeze/activate":
            admin_token = self._admin_token(gateway_result["request"]["headers"])
            election_id = str(payload.get("election_id", "election-2026"))
            reason = str(payload.get("reason", "admin-requested"))
            approvers = tuple(str(value) for value in payload.get("approvers", ()))
            state = self.control_plane.activate_freeze(election_id, reason, approvers)
            self.dependencies.election_state_manager.set_state(
                ElectionState(election_id=election_id, phase=state.phase, freeze_active=state.freeze_active)
            )
            return 200, {
                "route": "voting_service",
                "admin_token": admin_token.removeprefix("admin-"),
                "state": self._json_safe(state),
            }

        if normalized_path == "/api/v1/vote/admin/freeze/clear":
            admin_token = self._admin_token(gateway_result["request"]["headers"])
            election_id = str(payload.get("election_id", "election-2026"))
            reason = str(payload.get("reason", "admin-clearance"))
            approvers = tuple(str(value) for value in payload.get("approvers", ()))
            state = self.control_plane.clear_freeze(election_id, reason, approvers)
            self.dependencies.election_state_manager.set_state(
                ElectionState(election_id=election_id, phase=state.phase, freeze_active=state.freeze_active)
            )
            return 200, {
                "route": "voting_service",
                "admin_token": admin_token.removeprefix("admin-"),
                "state": self._json_safe(state),
            }

        if normalized_path == "/api/v1/vote/admin/offline-sync/stage":
            admin_token = self._admin_token(gateway_result["request"]["headers"])
            record = payload.get("record")
            if not isinstance(record, dict):
                raise ValueError("record must be an object")
            result = self.offline_sync_api.stage_record(record, operator_id=admin_token.removeprefix("admin-"))
            return 200, {
                "route": "voting_service",
                "admin_token": admin_token.removeprefix("admin-"),
                "queue_depth": result["queue_depth"],
                "record": self._json_safe(result["record"]),
            }

        if normalized_path == "/api/v1/vote/admin/offline-sync/queue":
            admin_token = self._admin_token(gateway_result["request"]["headers"])
            result = self.offline_sync_api.queue_status(operator_id=admin_token.removeprefix("admin-"))
            return 200, {
                "route": "voting_service",
                "admin_token": admin_token.removeprefix("admin-"),
                "queue_depth": result["queue_depth"],
                "queued_records": self._json_safe(result["queued_records"]),
            }

        if normalized_path == "/api/v1/vote/admin/offline-sync/flush":
            admin_token = self._admin_token(gateway_result["request"]["headers"])
            device_id = str(payload.get("device_id", "device-1"))
            remote_records = payload.get("remote_records", [])
            approvers = tuple(str(value) for value in payload.get("approvers", ()))
            if not isinstance(remote_records, list):
                raise ValueError("remote_records must be a list")
            private_key_pem = self.device_private_keys.setdefault(
                device_id,
                Phase1StandardCrypto().serialize_private_key(Phase1StandardCrypto().generate_rsa_private_key()),
            )
            if device_id not in self.device_public_keys:
                private_key = Phase1StandardCrypto().load_private_key(private_key_pem)
                self.device_public_keys[device_id] = Phase1StandardCrypto().serialize_public_key(private_key.public_key())
            result = self.offline_sync_api.flush(
                remote_records=remote_records,
                device_id=device_id,
                private_key_pem=private_key_pem,
                public_key_pem=self.device_public_keys[device_id],
                operator_id=admin_token.removeprefix("admin-"),
                approvers=approvers,
            )
            return 200, {
                "route": "voting_service",
                "admin_token": admin_token.removeprefix("admin-"),
                "queue_depth": result["queue_depth"],
                "artifacts": self._json_safe(result["artifacts"]),
                "manifest_valid": result["manifest_valid"],
            }

        if normalized_path == "/api/v1/vote/admin/offline-sync/approvals":
            admin_token = self._admin_token(gateway_result["request"]["headers"])
            operation_id = str(
                payload.get("operation_id") or gateway_result["request"].get("query", {}).get("operation_id", "")
            ) or None
            return 200, {
                "route": "voting_service",
                "admin_token": admin_token.removeprefix("admin-"),
                "approvals": self._json_safe(self.offline_sync_api.approval_history(operation_id)),
            }

        if normalized_path == "/api/v1/vote/observer/audit":
            observer_token = self._observer_token(gateway_result["request"]["headers"])
            entries = fetch_audit_entries(observer_token, self.dependencies.audit_logger)
            return 200, {
                "route": "voting_service",
                "entries": self._json_safe(entries),
                "audit_log_valid": verify_hash_chain(self.dependencies.audit_logger.entries()),
            }

        if normalized_path == "/api/v1/vote/observer/audit/export":
            observer_token = self._observer_token(gateway_result["request"]["headers"])
            export_payload = export_audit_log(observer_token, self.dependencies.audit_logger)
            return 200, {
                "route": "voting_service",
                "audit_log": json.loads(export_payload),
                "audit_log_valid": verify_hash_chain(self.dependencies.audit_logger.entries()),
            }

        if normalized_path.startswith("/api/v1/vote/observer/tally/"):
            observer_token = self._observer_token(gateway_result["request"]["headers"])
            election_id = normalized_path.rsplit("/", 1)[-1]
            votes = self.dependencies.vote_repository.list_by_election(election_id)
            tally = TallyService().tally(votes, self.tally_private_key_pem)
            return 200, {
                "route": "voting_service",
                "observer_token": observer_token.removeprefix("observer-"),
                "tally": observer_tally("observer", tally),
            }

        if normalized_path == "/api/v1/vote/observer/paper-reconcile":
            observer_token = self._observer_token(gateway_result["request"]["headers"])
            election_id = str(payload.get("election_id", "election-2026"))
            paper_ballots = payload.get("paper_ballots", [])
            if not isinstance(paper_ballots, list):
                raise ValueError("paper_ballots must be a list")
            votes = self.dependencies.vote_repository.list_by_election(election_id)
            digital_tally = TallyService().tally(votes, self.tally_private_key_pem)
            paper_counts = recount_ballots([str(ballot) for ballot in paper_ballots])
            return 200, {
                "route": "voting_service",
                "observer_token": observer_token.removeprefix("observer-"),
                "digital_tally": digital_tally,
                "paper_counts": paper_counts,
                "delta": reconcile(paper_counts, digital_tally),
            }

        if normalized_path == "/api/v1/vote/compliance/report":
            observer_token = self._observer_token(gateway_result["request"]["headers"])
            return 200, {
                "route": "voting_service",
                "observer_token": observer_token.removeprefix("observer-"),
                "report": generate_compliance_report(
                    self.dependencies.audit_logger,
                    offline_sync_operations=self.offline_sync_api.operation_history(),
                ),
            }

        if normalized_path == "/api/v1/vote/compliance/offline-sync-evidence":
            observer_token = self._observer_token(gateway_result["request"]["headers"])
            operation_id = str(
                payload.get("operation_id") or gateway_result["request"].get("query", {}).get("operation_id", "")
            ) or None
            case_id = str(
                payload.get("case_id") or gateway_result["request"].get("query", {}).get("case_id", "offline-sync-review")
            )
            device_id = str(
                payload.get("device_id") or gateway_result["request"].get("query", {}).get("device_id", "device-1")
            )
            private_key_pem = self.device_private_keys.setdefault(
                device_id,
                Phase1StandardCrypto().serialize_private_key(Phase1StandardCrypto().generate_rsa_private_key()),
            )
            if device_id not in self.device_public_keys:
                private_key = Phase1StandardCrypto().load_private_key(private_key_pem)
                self.device_public_keys[device_id] = Phase1StandardCrypto().serialize_public_key(private_key.public_key())
            operations = self.offline_sync_api.operation_history(operation_id)
            bundle = generate_offline_sync_evidence_bundle(
                case_id=case_id,
                operations=operations,
                actor=observer_token.removeprefix("observer-"),
                signing_key_pem=private_key_pem,
            )
            self.dependencies.audit_logger.append(
                "offline_sync_evidence_bundle_generated",
                {
                    "observer_id": observer_token.removeprefix("observer-"),
                    "operation_id": operation_id or "all",
                    "device_id": device_id,
                    "case_id": case_id,
                    "operation_count": len(operations),
                },
            )
            return 200, {
                "route": "voting_service",
                "observer_token": observer_token.removeprefix("observer-"),
                "bundle": self._json_safe(bundle.to_dict()),
            }

        if normalized_path == "/api/v1/vote/cast":
            token = str(payload.get("token", ""))
            ballot_id = str(payload.get("ballot_id", "ballot-2026"))
            election_id = str(payload.get("election_id", "election-2026"))
            device_id = str(payload.get("device_id", "device-1"))
            selections = payload.get("selections", {})
            if not isinstance(selections, dict):
                raise ValueError("selections must be an object")
            device_private_key_pem = self.device_private_keys.setdefault(
                device_id,
                Phase1StandardCrypto().serialize_private_key(Phase1StandardCrypto().generate_rsa_private_key()),
            )
            vote = cast_vote(
                election_state_manager=self.dependencies.election_state_manager,
                verification_gateway=self.verification_gateway,
                token_consumer=self.dependencies.token_consumer,
                replay_detector=self.dependencies.replay_detector,
                rate_limit_enforcer=self.dependencies.rate_limit_enforcer,
                time_sync_validator=self.dependencies.time_sync_validator,
                device_revocation_service=self.dependencies.device_revocation_service,
                device_signing_service=self.dependencies.device_signing_service,
                encryption_service=self.dependencies.encryption_service,
                crypto_provider=self.dependencies.crypto_provider,
                token=token,
                ballot_id=ballot_id,
                election_id=election_id,
                selections=selections,
                device_id=device_id,
                device_private_key_pem=device_private_key_pem,
                tally_public_key_pem=self.tally_public_key_pem,
                device_time=datetime.now(timezone.utc),
                trusted_time=datetime.now(timezone.utc),
                audit_logger=self.dependencies.audit_logger,
            )
            self.dependencies.result_hash_publisher.publish(
                election_id,
                {"encrypted_vote_digest": self.dependencies.crypto_provider.digest(vote.encrypted_vote)},
            )
            self.dependencies.vote_repository.save(vote)
            return 201, {"route": "voting_service", "vote": self._json_safe(vote.to_dict())}

        if normalized_path == "/api/v1/vote/emergency-freeze":
            reason = str(payload.get("reason", "operator-requested"))
            approvals = int(payload.get("approvals", 0))
            current_state = self.dependencies.election_state_manager.state
            updated_state, event = self.dependencies.emergency_freeze_service.activate(
                current_state,
                reason,
                approvals,
            )
            self.dependencies.election_state_manager.set_state(updated_state)
            return 200, {
                "route": "voting_service",
                "state": self._json_safe(self.dependencies.election_state_manager.state),
                "event": self._json_safe(event),
            }

        raise ValueError(f"No local handler for path: {normalized_path}")


def run_local_demo_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    """Start the local demo HTTP server for SecureVote PNG."""

    runtime = LocalGatewayRuntime.build()

    class Handler(BaseHTTPRequestHandler):
        def _read_body(self) -> str:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0:
                return ""
            return self.rfile.read(length).decode("utf-8")

        def _send(self, status_code: int, payload: dict[str, object]) -> None:
            body = json.dumps(payload, indent=2).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            self._handle()

        def do_POST(self) -> None:  # noqa: N802
            self._handle()

        def log_message(self, format: str, *args: object) -> None:
            return

        def _handle(self) -> None:
            try:
                status_code, payload = runtime.dispatch(
                    method=self.command,
                    path=self.path,
                    headers={key: value for key, value in self.headers.items()},
                    body=self._read_body(),
                )
            except PermissionError as exc:
                self._send(403, {"error": str(exc)})
                return
            except (KeyError, ValueError, json.JSONDecodeError) as exc:
                self._send(400, {"error": str(exc)})
                return
            except Exception as exc:  # pragma: no cover - defensive runtime fallback
                self._send(500, {"error": f"internal error: {exc}"})
                return
            self._send(status_code, payload)

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"SecureVote local demo server listening on http://{host}:{port}")
    for line in render_inventory_lines(LOCAL_RUNTIME_ENDPOINTS):
        print(line)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
