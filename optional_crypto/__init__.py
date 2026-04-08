"""Optional crypto is unavailable in Phase 1."""

from __future__ import annotations


def ensure_optional_crypto_disabled() -> None:
    raise RuntimeError("Optional crypto is disabled in Phase 1")


__all__ = ["ensure_optional_crypto_disabled"]
