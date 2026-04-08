"""Offline sync settings."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os


def _runtime_path(filename: str) -> str:
    runtime_dir = Path(os.getenv("OFFLINE_SYNC_RUNTIME_DIR", "data/runtime"))
    return str(runtime_dir / filename)


@dataclass(frozen=True)
class SyncSettings:
    sync_interval_seconds: int = 300
    max_batch_size: int = 100
    max_retry_attempts: int = 5
    compression_enabled: bool = True
    use_durable_approval_tracker: bool = field(
        default_factory=lambda: os.getenv("OFFLINE_SYNC_USE_DURABLE_APPROVAL_TRACKER", "true").lower() == "true"
    )
    approval_tracker_path: str = field(default_factory=lambda: _runtime_path("offline_sync_approvals.sqlite3"))
    use_durable_operation_history: bool = field(
        default_factory=lambda: os.getenv("OFFLINE_SYNC_USE_DURABLE_OPERATION_HISTORY", "true").lower() == "true"
    )
    operation_history_path: str = field(default_factory=lambda: _runtime_path("offline_sync_operations.sqlite3"))
