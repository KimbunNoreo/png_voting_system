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


def generate_evidence_bundle(case_id: str, artifacts: list[dict[str, object]], actor: str) -> EvidenceBundle:
    custody = (record_custody_event(actor, "bundle_created"),)
    tagged_artifacts = tuple(
        embed_metadata(sanitize_audit_payload(artifact), {"case_id": case_id, "actor": actor}) for artifact in artifacts
    )
    statement = generate_statement(case_id, verified=True)
    return EvidenceBundle(case_id=case_id, artifacts=tagged_artifacts, custody_events=custody, verification_statement=statement)


def generate_offline_sync_evidence_bundle(
    case_id: str,
    operations: list[dict[str, object]],
    actor: str,
    signing_key_pem: str,
) -> EvidenceBundle:
    """Build a court-ready evidence bundle around signed offline sync history."""

    signed_export = create_signed_offline_sync_export(operations, signing_key_pem)
    export_payload = json.loads(signed_export["payload"])
    artifacts = [
        {
            "artifact_id": f"{case_id}-offline-sync-export",
            "kind": "offline_sync_export",
            "service": export_payload["service"],
            "phase": export_payload["phase"],
            "operations": export_payload["operations"],
            "signature": signed_export["signature"],
        }
    ]
    custody = (
        record_custody_event(actor, "offline_sync_export_signed"),
        record_custody_event(actor, "bundle_created"),
    )
    tagged_artifacts = tuple(
        embed_metadata(
            sanitize_audit_payload(artifact),
            {"case_id": case_id, "actor": actor, "artifact_role": "offline_sync_reconciliation"},
        )
        for artifact in artifacts
    )
    statement = generate_statement(case_id, verified=True)
    return EvidenceBundle(case_id=case_id, artifacts=tagged_artifacts, custody_events=custody, verification_statement=statement)
