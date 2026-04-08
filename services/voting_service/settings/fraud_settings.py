from dataclasses import dataclass
@dataclass(frozen=True)
class FraudSettings:
    allow_ai_assistance: bool = False
    max_votes_per_device_per_minute: int = 10
    max_votes_per_token_per_minute: int = 1