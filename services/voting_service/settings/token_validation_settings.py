from dataclasses import dataclass
@dataclass(frozen=True)
class TokenValidationSettings:
    require_one_time_use: bool = True
    max_clock_skew_seconds: int = 30