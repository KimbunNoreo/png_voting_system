"""Conflict resolution for offline vote synchronization."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from services.audit_service.payload_sanitizer import sanitize_audit_payload


@dataclass(frozen=True)
class ConflictDecision:
    token_hash: str
    winner_created_at: str
    discarded_created_at: str
    resolution: str = "keep_earliest"


@dataclass(frozen=True)
class ConflictReport:
    merged_count: int
    conflict_count: int
    decisions: tuple[ConflictDecision, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "merged_count": self.merged_count,
            "conflict_count": self.conflict_count,
            "decisions": [asdict(decision) for decision in self.decisions],
        }


def resolve_conflicts(
    local_records: list[dict[str, object]],
    remote_records: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Merge by token hash and keep the earliest accepted vote per token."""

    merged, _ = resolve_conflicts_with_report(local_records, remote_records)
    return merged


def resolve_conflicts_with_report(
    local_records: list[dict[str, object]],
    remote_records: list[dict[str, object]],
) -> tuple[list[dict[str, object]], ConflictReport]:
    """Merge records and produce a structured conflict report."""

    merged: dict[str, dict[str, object]] = {}
    decisions: list[ConflictDecision] = []
    for raw_record in local_records + remote_records:
        record = sanitize_audit_payload(raw_record)
        token_hash = str(record["token_hash"])
        existing = merged.get(token_hash)
        if existing is None:
            merged[token_hash] = record
            continue
        existing_created_at = str(existing.get("created_at", ""))
        record_created_at = str(record.get("created_at", ""))
        if record_created_at < existing_created_at:
            decisions.append(
                ConflictDecision(
                    token_hash=token_hash,
                    winner_created_at=record_created_at,
                    discarded_created_at=existing_created_at,
                )
            )
            merged[token_hash] = record
        else:
            decisions.append(
                ConflictDecision(
                    token_hash=token_hash,
                    winner_created_at=existing_created_at,
                    discarded_created_at=record_created_at,
                )
            )
    report = ConflictReport(
        merged_count=len(merged),
        conflict_count=len(decisions),
        decisions=tuple(decisions),
    )
    return list(merged.values()), report
