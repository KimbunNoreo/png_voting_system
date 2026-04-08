"""Migration signature tracking model."""
from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class MigrationSignature:
    migration_name: str
    signature: str
    signer_kid: str
    verified: bool