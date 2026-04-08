"""Standalone HTTP runtime for the offline sync service."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from typing import Any

from config import get_settings
from legal_evidence import generate_offline_sync_evidence_bundle
from legal_evidence.signed_offline_sync_export import create_signed_offline_sync_export
from services.audit_service import WORMLogger
from services.endpoint_inventory import OFFLINE_SYNC_RUNTIME_ENDPOINTS, render_inventory_lines
from services.offline_sync_service.factory import OfflineSyncDependencies, build_offline_sync_dependencies
from services.voting_service.crypto.phase1_standard import Phase1StandardCrypto


class OfflineSyncServiceRuntime:
    """Minimal HTTP runtime for operator-facing offline sync workflows."""

    def __init__(
        self,
        *,
        dependencies: OfflineSyncDependencies | None = None,
        device_private_keys: dict[str, str] | None = None,
        device_public_keys: dict[str, str] | None = None,
    ) -> None:
        self.dependencies = dependencies or self._build_dependencies()
        self.device_private_keys = device_private_keys or {}
        self.device_public_keys = device_public_keys or {}
        if "device-1" not in self.device_private_keys or "device-1" not in self.device_public_keys:
            crypto = Phase1StandardCrypto()
            keypair = crypto.generate_rsa_private_key()
            self.device_private_keys.setdefault("device-1", crypto.serialize_private_key(keypair))
            self.device_public_keys.setdefault("device-1", crypto.serialize_public_key(keypair.public_key()))

    @staticmethod
    def _build_dependencies() -> OfflineSyncDependencies:
        settings = get_settings()
        if settings.audit_service.use_durable_worm_log:
            audit_logger = WORMLogger.with_sqlite_store(settings.audit_service.worm_log_path)
        else:
            audit_logger = WORMLogger()
        return build_offline_sync_dependencies(audit_logger=audit_logger)

    def _parse_body(self, body: str) -> dict[str, object]:
        if not body:
            return {}
        parsed = json.loads(body)
        if not isinstance(parsed, dict):
            raise ValueError("JSON request body must be an object")
        return parsed

    def _admin_token(self, headers: dict[str, str]) -> str:
        authorization = headers.get("Authorization", "")
        scheme, _, token = authorization.partition(" ")
        if scheme != "Bearer" or not token.startswith("admin-"):
            raise PermissionError("Administrator token is required")
        return token

    def _audit(self, event_type: str, payload: dict[str, object]) -> None:
        if self.dependencies.audit_logger is not None:
            self.dependencies.audit_logger.append(event_type, payload)

    def readiness(self) -> dict[str, object]:
        """Expose readiness details for orchestration and operators."""

        approval_store_name = self.dependencies.approval_tracker.store.__class__.__name__
        return {
            "status": "ready",
            "service": "offline_sync_service",
            "phase": "phase1",
            "queue_depth": len(self.dependencies.engine.queue),
            "approval_store": approval_store_name,
            "operation_store": self.dependencies.operation_history.store.__class__.__name__,
        }

    def status_report(self) -> dict[str, object]:
        """Expose operator-facing service status and recent activity."""

        approval_history = self.dependencies.operator_api.approval_history()
        latest_approval = approval_history[-1] if approval_history else None
        operation_history = self.dependencies.operator_api.operation_history()
        latest_operation = operation_history[-1] if operation_history else None
        latest_audit_event = None
        latest_evidence_event = None
        if self.dependencies.audit_logger is not None:
            entries = self.dependencies.audit_logger.entries()
            latest_audit_event = entries[-1].event_type if entries else None
            latest_evidence_event = next(
                (
                    entry.event_type
                    for entry in reversed(entries)
                    if entry.event_type in {"offline_sync_operation_exported", "offline_sync_evidence_bundle_generated"}
                ),
                None,
            )
        return {
            "status": "ok",
            "service": "offline_sync_service",
            "phase": "phase1",
            "queue_depth": len(self.dependencies.engine.queue),
            "approval_store": self.dependencies.approval_tracker.store.__class__.__name__,
            "operation_store": self.dependencies.operation_history.store.__class__.__name__,
            "approval_history_count": len(approval_history),
            "latest_approval": latest_approval,
            "operation_history_count": len(operation_history),
            "offline_sync_conflict_total": sum(int(operation.get("conflict_count", 0)) for operation in operation_history),
            "latest_operation": latest_operation,
            "latest_audit_event": latest_audit_event,
            "latest_evidence_event": latest_evidence_event,
        }

    def dispatch(self, method: str, path: str, headers: dict[str, str], body: str = "") -> tuple[int, dict[str, object]]:
        if path == "/health":
            return 200, {"status": "ok", "service": "offline_sync_service", "phase": "phase1"}
        if path == "/ready":
            return 200, self.readiness()

        admin_token = self._admin_token(headers)
        payload = self._parse_body(body)

        if method == "POST" and path == "/api/v1/offline-sync/stage":
            record = payload.get("record")
            if not isinstance(record, dict):
                raise ValueError("record must be an object")
            result = self.dependencies.operator_api.stage_record(record, operator_id=admin_token.removeprefix("admin-"))
            return 200, {
                "admin_token": admin_token.removeprefix("admin-"),
                "queue_depth": result["queue_depth"],
                "record": result["record"],
            }

        if method == "GET" and path == "/api/v1/offline-sync/queue":
            result = self.dependencies.operator_api.queue_status(operator_id=admin_token.removeprefix("admin-"))
            return 200, {
                "admin_token": admin_token.removeprefix("admin-"),
                "queue_depth": result["queue_depth"],
                "queued_records": result["queued_records"],
            }

        if method == "POST" and path == "/api/v1/offline-sync/flush":
            device_id = str(payload.get("device_id", "device-1"))
            remote_records = payload.get("remote_records", [])
            approvers = tuple(str(value) for value in payload.get("approvers", ()))
            if not isinstance(remote_records, list):
                raise ValueError("remote_records must be a list")
            private_key_pem = self.device_private_keys[device_id]
            public_key_pem = self.device_public_keys[device_id]
            result = self.dependencies.operator_api.flush(
                remote_records=remote_records,
                device_id=device_id,
                private_key_pem=private_key_pem,
                public_key_pem=public_key_pem,
                operator_id=admin_token.removeprefix("admin-"),
                approvers=approvers,
            )
            return 200, {
                "admin_token": admin_token.removeprefix("admin-"),
                "queue_depth": result["queue_depth"],
                "artifacts": result["artifacts"],
                "manifest_valid": result["manifest_valid"],
            }

        if method == "GET" and path == "/api/v1/offline-sync/approvals":
            operation_id = str(payload.get("operation_id", "")) or None
            return 200, {
                "admin_token": admin_token.removeprefix("admin-"),
                "approvals": self.dependencies.operator_api.approval_history(operation_id),
            }

        if method == "GET" and path == "/api/v1/offline-sync/operations":
            operation_id = str(payload.get("operation_id", "")) or None
            return 200, {
                "admin_token": admin_token.removeprefix("admin-"),
                "operations": self.dependencies.operator_api.operation_history(operation_id),
            }

        if method == "GET" and path == "/api/v1/offline-sync/operations/export":
            operation_id = str(payload.get("operation_id", "")) or None
            device_id = str(payload.get("device_id", "device-1"))
            private_key_pem = self.device_private_keys[device_id]
            operations = self.dependencies.operator_api.operation_history(operation_id)
            export = create_signed_offline_sync_export(
                operations,
                private_key_pem,
            )
            self._audit(
                "offline_sync_operation_exported",
                {
                    "operator_id": admin_token.removeprefix("admin-"),
                    "operation_id": operation_id or "all",
                    "device_id": device_id,
                    "operation_count": len(operations),
                },
            )
            return 200, {
                "admin_token": admin_token.removeprefix("admin-"),
                "export": export,
            }

        if method == "GET" and path == "/api/v1/offline-sync/operations/evidence-bundle":
            operation_id = str(payload.get("operation_id", "")) or None
            device_id = str(payload.get("device_id", "device-1"))
            case_id = str(payload.get("case_id", "offline-sync-review"))
            private_key_pem = self.device_private_keys[device_id]
            operations = self.dependencies.operator_api.operation_history(operation_id)
            bundle = generate_offline_sync_evidence_bundle(
                case_id=case_id,
                operations=operations,
                actor=admin_token.removeprefix("admin-"),
                signing_key_pem=private_key_pem,
            )
            self._audit(
                "offline_sync_evidence_bundle_generated",
                {
                    "operator_id": admin_token.removeprefix("admin-"),
                    "operation_id": operation_id or "all",
                    "device_id": device_id,
                    "case_id": case_id,
                    "operation_count": len(operations),
                },
            )
            return 200, {
                "admin_token": admin_token.removeprefix("admin-"),
                "bundle": bundle.to_dict(),
            }

        if method == "GET" and path == "/api/v1/offline-sync/status":
            return 200, {
                "admin_token": admin_token.removeprefix("admin-"),
                "report": self.status_report(),
            }

        raise ValueError(f"No offline sync handler for path: {path}")


def run_offline_sync_server(host: str = "127.0.0.1", port: int = 8100) -> None:
    """Start the standalone offline sync service server."""

    runtime = OfflineSyncServiceRuntime()

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
            except Exception as exc:  # pragma: no cover
                self._send(500, {"error": f"internal error: {exc}"})
                return
            self._send(status_code, payload)

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Offline sync service listening on http://{host}:{port}")
    for line in render_inventory_lines(OFFLINE_SYNC_RUNTIME_ENDPOINTS):
        print(line)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
