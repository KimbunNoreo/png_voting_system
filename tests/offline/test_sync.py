from __future__ import annotations

import unittest

from services.offline_sync_service.sync.engine import SyncEngine
from services.voting_service.crypto.phase1_standard import Phase1StandardCrypto


class OfflineSyncTests(unittest.TestCase):
    def test_sync_engine_merges_records_by_token_hash(self) -> None:
        engine = SyncEngine()
        engine.stage_vote({"token_hash": "t1", "created_at": "2026-04-05T00:00:00Z", "vote": "local"})
        merged = engine.flush(
            [{"token_hash": "t1", "created_at": "2026-04-05T00:01:00Z", "vote": "remote"}]
        )
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["vote"], "local")

    def test_sync_engine_redacts_sensitive_fields_before_storage(self) -> None:
        engine = SyncEngine()
        engine.stage_vote(
            {
                "token_hash": "t2",
                "created_at": "2026-04-05T00:00:00Z",
                "vote": "local",
                "token": "raw-token",
                "name": "Sensitive Name",
                "nested": {"address": "Sensitive Address"},
            }
        )
        records = engine.local_store.fetch_all()
        self.assertEqual(records[0]["token"], "[redacted]")
        self.assertEqual(records[0]["name"], "[redacted]")
        self.assertEqual(records[0]["nested"]["address"], "[redacted]")

    def test_sync_engine_flush_with_artifacts_returns_signed_manifest_and_report(self) -> None:
        engine = SyncEngine()
        engine.stage_vote({"token_hash": "t1", "created_at": "2026-04-05T00:00:00Z", "vote": "local"})
        crypto = Phase1StandardCrypto()
        private_key = crypto.generate_rsa_private_key()
        private_pem = crypto.serialize_private_key(private_key)
        result = engine.flush_with_artifacts(
            [{"token_hash": "t1", "created_at": "2026-04-05T00:01:00Z", "vote": "remote"}],
            device_id="device-1",
            private_key_pem=private_pem,
        )
        self.assertEqual(len(result["records"]), 1)
        self.assertEqual(result["manifest"]["device_id"], "device-1")
        self.assertEqual(result["manifest"]["record_count"], 1)
        self.assertEqual(result["conflict_report"]["conflict_count"], 1)


if __name__ == "__main__":
    unittest.main()
