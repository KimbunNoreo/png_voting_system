"""Legal evidence test package shim for unittest discovery.

This package name collides with the top-level ``legal_evidence`` application
package when ``python -m unittest discover -s tests`` uses ``tests`` as the
import root. Extend the package search path so application imports still
resolve to the real implementation modules.
"""

from __future__ import annotations

from pathlib import Path

_REAL_PACKAGE_DIR = Path(__file__).resolve().parents[2] / "legal_evidence"
if str(_REAL_PACKAGE_DIR) not in __path__:
    __path__.append(str(_REAL_PACKAGE_DIR))

from .evidence_bundle_generator import EvidenceBundle, generate_evidence_bundle, generate_offline_sync_evidence_bundle

__all__ = ["EvidenceBundle", "generate_evidence_bundle", "generate_offline_sync_evidence_bundle"]
