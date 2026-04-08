"""Reproducible build verification helpers."""

from __future__ import annotations

import hashlib


def build_digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def verify_build(content: str, expected_digest: str) -> bool:
    return build_digest(content) == expected_digest
