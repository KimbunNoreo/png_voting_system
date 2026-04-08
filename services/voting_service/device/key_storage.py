from services.voting_service.crypto.phase1_standard import Phase1StandardCrypto
class DeviceKeyStorage:
    def __init__(self) -> None:
        self._crypto = Phase1StandardCrypto(); self._private_key = self._crypto.generate_rsa_private_key()
    def private_key_pem(self) -> str:
        return self._crypto.serialize_private_key(self._private_key)
    def public_key_pem(self) -> str:
        return self._crypto.serialize_public_key(self._private_key.public_key())