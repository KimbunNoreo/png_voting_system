from dataclasses import dataclass
@dataclass(frozen=True)
class DeviceSigningSettings:
    signing_algorithm: str = "RSA-PSS-SHA256"
    require_tpm_backed_keys: bool = True