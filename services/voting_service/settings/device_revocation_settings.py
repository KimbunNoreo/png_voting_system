from dataclasses import dataclass
@dataclass(frozen=True)
class DeviceRevocationSettings:
    check_before_vote: bool = True
    reattestation_hours: int = 24