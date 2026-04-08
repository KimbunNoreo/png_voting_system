"""Standalone public verifier entry point."""

from __future__ import annotations

from public_verifier_cli.audit_log_validator import validate_audit_log
from public_verifier_cli.hash_checker import verify_result_hash
from public_verifier_cli.paper_trail_comparator import compare_counts
from services.audit_service.logger.worm_logger import AuditEntry


def run_verification(
    election_id: str,
    tally: dict[str, int],
    published_hash: str,
    audit_entries: list[AuditEntry],
    paper_counts: dict[str, int],
) -> dict[str, object]:
    return {
        "result_hash_valid": verify_result_hash(election_id, tally, published_hash),
        "audit_log_valid": validate_audit_log(audit_entries),
        "paper_vs_digital_delta": compare_counts(paper_counts, tally),
    }
