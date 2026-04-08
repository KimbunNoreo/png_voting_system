from __future__ import annotations

from pathlib import Path
import unittest
from uuid import uuid4

from election_state.control_plane import ElectionControlPlane, ElectionControlSnapshot, SQLiteElectionControlStore
from services.audit_service import WORMLogger


class ElectionControlPlaneTests(unittest.TestCase):
    def test_phase_transition_requires_two_approvers(self) -> None:
        control_plane = ElectionControlPlane(
            initial_state=ElectionControlSnapshot("e1", "registration", False, ""),
            audit_logger=WORMLogger(),
        )
        with self.assertRaises(ValueError):
            control_plane.transition_phase("e1", "verification", ("official-1",))

    def test_sqlite_control_plane_survives_restart(self) -> None:
        runtime_dir = Path("data") / "test_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        database_path = runtime_dir / f"control_plane_{uuid4().hex}.sqlite3"
        phase_audit_path = runtime_dir / f"control_plane_phase_audit_{uuid4().hex}.sqlite3"
        try:
            first = ElectionControlPlane.with_sqlite_store(
                str(database_path),
                initial_state=ElectionControlSnapshot("e1", "registration", False, ""),
                audit_logger=WORMLogger(),
                phase_audit_path=str(phase_audit_path),
            )
            first.transition_phase("e1", "verification", ("official-1", "official-2"))
            first.activate_freeze("e1", "incident", ("official-1", "official-2", "official-3"))

            second = ElectionControlPlane.with_sqlite_store(
                str(database_path),
                initial_state=ElectionControlSnapshot("e1", "registration", False, ""),
                phase_audit_path=str(phase_audit_path),
            )
            state = second.get_state("e1")
            self.assertEqual(state.phase, "verification")
            self.assertTrue(state.freeze_active)
            self.assertEqual(len(second.phase_history("e1")), 1)
        finally:
            if database_path.exists():
                database_path.unlink()
            if phase_audit_path.exists():
                phase_audit_path.unlink()

    def test_sqlite_control_plane_store_type_is_exposed(self) -> None:
        runtime_dir = Path("data") / "test_runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        database_path = runtime_dir / f"control_plane_store_{uuid4().hex}.sqlite3"
        try:
            control_plane = ElectionControlPlane.with_sqlite_store(
                str(database_path),
                initial_state=ElectionControlSnapshot("e1", "voting", False, ""),
            )
            self.assertIsInstance(control_plane.store, SQLiteElectionControlStore)
        finally:
            if database_path.exists():
                database_path.unlink()


if __name__ == "__main__":
    unittest.main()
