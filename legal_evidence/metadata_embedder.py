"""Metadata embedding helpers for evidence bundles."""

from __future__ import annotations


def embed_metadata(document: dict[str, object], metadata: dict[str, object]) -> dict[str, object]:
    enriched = dict(document)
    enriched["metadata"] = dict(metadata)
    return enriched
