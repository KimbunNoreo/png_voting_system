from dataclasses import dataclass
@dataclass(frozen=True)
class EncryptionSettings:
    scheme: str = "AES-256-GCM"
    key_exchange: str = "RSA-4096"
    signing_algorithm: str = "RSA-PSS-SHA256"