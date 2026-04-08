"""Operational smoke test for offline sync behavior."""

from __future__ import annotations

from services.offline_sync_service.sync.engine import SyncEngine


def run_smoke_test() -> list[dict[str, object]]:
    engine = SyncEngine()
    engine.stage_vote({"token_hash": "smoke-token", "created_at": "2026-04-05T00:00:00Z", "vote": "local"})
    return engine.flush([])
