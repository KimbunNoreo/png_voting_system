"""Structured error returned by the NID service."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NIDError:
    code: str
    message: str
    retryable: bool = False