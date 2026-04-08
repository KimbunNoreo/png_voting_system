"""Independent audit log validation."""

from __future__ import annotations

from services.audit_service.detection.tamper import verify_hash_chain
from services.audit_service.logger.worm_logger import AuditEntry


def validate_audit_log(entries: list[AuditEntry]) -> bool:
    return verify_hash_chain(entries)
