"""Readiness test profiles for repeatable operational verification."""

from __future__ import annotations

from dataclasses import dataclass
import unittest


READINESS_PROFILES: dict[str, tuple[str, ...]] = {
    "quick": (
        "tests.security.test_manage_entrypoint",
        "tests.security.test_gateway_security",
        "tests.integration.test_gateway_routing",
        "tests.integration.test_nid_voting_flow",
        "tests.security.test_emergency_freeze",
        "tests.security.test_token_replay_global",
    ),
    "core": (
        "tests.security.test_gateway_security",
        "tests.integration.test_local_runtime",
        "tests.integration.test_offline_sync_runtime",
        "tests.security.test_token_replay_global",
        "tests.offline.test_operator_api",
        "tests.voting.test_public_verification",
        "tests.legal_evidence.test_evidence_bundle",
    ),
}


@dataclass(frozen=True)
class ReadinessResult:
    """Structured outcome from a readiness profile execution."""

    profile: str
    tests_run: int
    failures: int
    errors: int
    successful: bool


def run_readiness_suite(profile: str = "core", *, verbosity: int = 2) -> ReadinessResult:
    """Execute a named readiness profile and return aggregate outcome details."""

    normalized = profile.strip().lower()
    loader = unittest.defaultTestLoader
    if normalized == "full":
        suite = loader.discover("tests")
    else:
        test_names = READINESS_PROFILES.get(normalized)
        if test_names is None:
            allowed = ", ".join(sorted((*READINESS_PROFILES.keys(), "full")))
            raise ValueError(f"Unknown readiness profile: {profile}. Allowed profiles: {allowed}")
        suite = loader.loadTestsFromNames(list(test_names))

    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    return ReadinessResult(
        profile=normalized,
        tests_run=result.testsRun,
        failures=len(result.failures),
        errors=len(result.errors),
        successful=result.wasSuccessful(),
    )
