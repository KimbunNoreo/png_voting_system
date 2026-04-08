from __future__ import annotations

from pathlib import Path
import unittest

import yaml


class APIContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract_path = Path("docs/api_contract.yaml")
        self.document = yaml.safe_load(self.contract_path.read_text(encoding="utf-8"))
        self.local_runtime_source = Path("services/api_gateway/local_runtime.py").read_text(encoding="utf-8")
        self.offline_runtime_source = Path("services/offline_sync_service/runtime.py").read_text(encoding="utf-8")

    def test_contract_is_valid_yaml_with_openapi_header(self) -> None:
        self.assertIsInstance(self.document, dict)
        self.assertEqual(self.document.get("openapi"), "3.0.3")
        self.assertIn("paths", self.document)
        self.assertIn("components", self.document)

    def test_contract_contains_expected_runtime_surfaces(self) -> None:
        paths = self.document["paths"]
        for path in (
            "/health",
            "/ready",
            "/api/v1/vote/compliance/report",
            "/api/v1/vote/compliance/offline-sync-evidence",
            "/api/v1/offline-sync/status",
            "/api/v1/offline-sync/operations/export",
            "/api/v1/offline-sync/operations/evidence-bundle",
        ):
            self.assertIn(path, paths)

    def test_internal_refs_resolve(self) -> None:
        for ref in self._collect_refs(self.document):
            self.assertTrue(ref.startswith("#/"), f"Only local refs are supported in this contract: {ref}")
            resolved = self._resolve_ref(self.document, ref)
            self.assertIsNotNone(resolved, f"Unresolved OpenAPI ref: {ref}")

    def test_contract_offline_sync_paths_exist_in_runtime_sources(self) -> None:
        contract_paths = self.document["paths"]
        runtime_backed_paths = {
            "/health": self.local_runtime_source,
            "/ready": self.offline_runtime_source,
            "/api/v1/vote/compliance/report": self.local_runtime_source,
            "/api/v1/vote/compliance/offline-sync-evidence": self.local_runtime_source,
            "/api/v1/vote/admin/offline-sync/stage": self.local_runtime_source,
            "/api/v1/vote/admin/offline-sync/queue": self.local_runtime_source,
            "/api/v1/vote/admin/offline-sync/flush": self.local_runtime_source,
            "/api/v1/vote/admin/offline-sync/approvals": self.local_runtime_source,
            "/api/v1/offline-sync/status": self.offline_runtime_source,
            "/api/v1/offline-sync/stage": self.offline_runtime_source,
            "/api/v1/offline-sync/queue": self.offline_runtime_source,
            "/api/v1/offline-sync/flush": self.offline_runtime_source,
            "/api/v1/offline-sync/approvals": self.offline_runtime_source,
            "/api/v1/offline-sync/operations": self.offline_runtime_source,
            "/api/v1/offline-sync/operations/export": self.offline_runtime_source,
            "/api/v1/offline-sync/operations/evidence-bundle": self.offline_runtime_source,
        }
        for path, source in runtime_backed_paths.items():
            self.assertIn(path, contract_paths, f"Path missing from contract: {path}")
            self.assertIn(path, source, f"Path missing from runtime source: {path}")

    def test_contract_parameterized_paths_match_runtime_prefixes(self) -> None:
        contract_paths = self.document["paths"]
        parameterized_runtime_paths = {
            "/api/v1/vote/public-result/{election_id}": (self.local_runtime_source, '"/api/v1/vote/public-result/"'),
            "/api/v1/vote/observer/tally/{election_id}": (self.local_runtime_source, '"/api/v1/vote/observer/tally/"'),
            "/api/v1/vote/admin/state/{election_id}": (self.local_runtime_source, '"/api/v1/vote/admin/state/"'),
        }
        for contract_path, (source, runtime_prefix_literal) in parameterized_runtime_paths.items():
            self.assertIn(contract_path, contract_paths, f"Parameterized path missing from contract: {contract_path}")
            self.assertIn(runtime_prefix_literal, source, f"Runtime prefix missing for path: {contract_path}")

    def _collect_refs(self, node: object) -> list[str]:
        refs: list[str] = []
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "$ref" and isinstance(value, str):
                    refs.append(value)
                else:
                    refs.extend(self._collect_refs(value))
        elif isinstance(node, list):
            for item in node:
                refs.extend(self._collect_refs(item))
        return refs

    def _resolve_ref(self, document: dict[str, object], ref: str) -> object | None:
        current: object = document
        for segment in ref.removeprefix("#/").split("/"):
            if not isinstance(current, dict) or segment not in current:
                return None
            current = current[segment]
        return current


if __name__ == "__main__":
    unittest.main()
