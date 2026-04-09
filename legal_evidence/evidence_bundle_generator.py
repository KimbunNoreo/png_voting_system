"""Court-ready evidence bundle generation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json

from services.audit_service.payload_sanitizer import sanitize_audit_payload
from legal_evidence.chain_of_custody_tracker import CustodyEvent, record_custody_event
from legal_evidence.metadata_embedder import embed_metadata
from legal_evidence.signed_offline_sync_export import create_signed_offline_sync_export
from legal_evidence.verification_statement_generator import generate_statement


@dataclass(frozen=True)
class EvidenceBundle:
    case_id: str
    artifacts: tuple[dict[str, object], ...]
    custody_events: tuple[CustodyEvent, ...]
    verification_statement: str

    def to_dict(self) -> dict[str, object]:
        return {
            "case_id": self.case_id,
            "artifacts": list(self.artifacts),
            "custody_events": [asdict(event) for event in self.custody_events],
            "verification_statement": self.verification_statement,
        }


MAX_CASE_ID_LENGTH = 128
MAX_ACTOR_LENGTH = 128
MAX_ARTIFACTS = 5000


def _validate_case_id(case_id: str) -> str:
    normalized = case_id.strip()
    if not normalized:
        raise ValueError("Case ID is required")
    if len(normalized) > MAX_CASE_ID_LENGTH:
        raise ValueError("Case ID is too long")
    return normalized


def _validate_actor(actor: str) -> str:
    normalized = actor.strip()
    if not normalized:
        raise ValueError("Actor is required")
    if len(normalized) > MAX_ACTOR_LENGTH:
        raise ValueError("Actor is too long")
    return normalized


def _validate_artifacts(artifacts: list[dict[str, object]]) -> list[dict[str, object]]:
    if not artifacts:
        raise ValueError("At least one evidence artifact is required")
    if len(artifacts) > MAX_ARTIFACTS:
        raise ValueError("Too many artifacts in a single evidence bundle")
    return artifacts


def generate_evidence_bundle(case_id: str, artifacts: list[dict[str, object]], actor: str) -> EvidenceBundle:
    normalized_case_id = _validate_case_id(case_id)
    normalized_actor = _validate_actor(actor)
    validated_artifacts = _validate_artifacts(artifacts)
    custody = (record_custody_event(normalized_actor, "bundle_created"),)
    tagged_artifacts = tuple(
        embed_metadata(
            sanitize_audit_payload(artifact),
            {"case_id": normalized_case_id, "actor": normalized_actor},
        )
        for artifact in validated_artifacts
    )
    statement = generate_statement(normalized_case_id, verified=True)
    return EvidenceBundle(
        case_id=normalized_case_id,
        artifacts=tagged_artifacts,
        custody_events=custody,
        verification_statement=statement,
    )


def generate_offline_sync_evidence_bundle(
    case_id: str,
    operations: list[dict[str, object]],
    actor: str,
    signing_key_pem: str,
) -> EvidenceBundle:
    """Build a court-ready evidence bundle around signed offline sync history."""

    normalized_case_id = _validate_case_id(case_id)
    normalized_actor = _validate_actor(actor)

    signed_export = create_signed_offline_sync_export(operations, signing_key_pem)
    export_payload = json.loads(signed_export["payload"])
    artifacts = [
        {
            "artifact_id": f"{normalized_case_id}-offline-sync-export",
            "kind": "offline_sync_export",
            "service": export_payload["service"],
            "phase": export_payload["phase"],
            "operations": export_payload["operations"],
            "signature": signed_export["signature"],
        }
    ]
    custody = (
        record_custody_event(normalized_actor, "offline_sync_export_signed"),
        record_custody_event(normalized_actor, "bundle_created"),
    )
    tagged_artifacts = tuple(
        embed_metadata(
            sanitize_audit_payload(artifact),
            {"case_id": normalized_case_id, "actor": normalized_actor, "artifact_role": "offline_sync_reconciliation"},
        )
        for artifact in artifacts
    )
    statement = generate_statement(normalized_case_id, verified=True)
    return EvidenceBundle(
        case_id=normalized_case_id,
        artifacts=tagged_artifacts,
        custody_events=custody,
        verification_statement=statement,
    )
