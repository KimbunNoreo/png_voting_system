from dataclasses import dataclass
@dataclass(frozen=True)
class RateLimitSettings:
    per_token_per_minute: int = 1
    per_device_per_minute: int = 10