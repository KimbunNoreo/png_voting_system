from dataclasses import dataclass
@dataclass(frozen=True)
class NIDClientSettings:
    require_external_validation: bool = True
    cache_ttl_seconds: int = 300