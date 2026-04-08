"""Audit service settings."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os


def _runtime_path(filename: str) -> str:
    runtime_dir = Path(os.getenv("AUDIT_RUNTIME_DIR", "data/runtime"))
    return str(runtime_dir / filename)


@dataclass(frozen=True)
class AuditSettings:
    retention_days: int = 3650
    export_signatures_required: bool = True
    observer_read_only: bool = True
    use_durable_worm_log: bool = field(default_factory=lambda: os.getenv("AUDIT_USE_DURABLE_WORM_LOG", "true").lower() == "true")
    worm_log_path: str = field(default_factory=lambda: _runtime_path("audit_log.sqlite3"))
