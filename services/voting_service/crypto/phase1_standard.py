"""Phase 1 cryptographic implementation using proven primitives only."""
from __future__ import annotations
import base64, json, os
from typing import Any
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
class Phase1StandardCrypto:
    def generate_rsa_private_key(self) -> rsa.RSAPrivateKey:
        return rsa.generate_private_key(public_exponent=65537, key_size=4096)
    def serialize_private_key(self, private_key: rsa.RSAPrivateKey) -> str:
        return private_key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption()).decode("utf-8")
    def serialize_public_key(self, public_key: rsa.RSAPublicKey) -> str:
        return public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo).decode("utf-8")
    def load_private_key(self, pem: str) -> rsa.RSAPrivateKey:
        return serialization.load_pem_private_key(pem.encode("utf-8"), password=None)
    def load_public_key(self, pem: str) -> rsa.RSAPublicKey:
        return serialization.load_pem_public_key(pem.encode("utf-8"))
    def encrypt(self, payload: dict[str, Any], public_key_pem: str) -> dict[str, str]:
        plaintext = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        aes_key = AESGCM.generate_key(bit_length=256)
        nonce = os.urandom(12)
        ciphertext = AESGCM(aes_key).encrypt(nonce, plaintext, None)
        encrypted_key = self.load_public_key(public_key_pem).encrypt(aes_key, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
        return {"encrypted_vote": base64.b64encode(ciphertext[:-16]).decode("utf-8"), "tag": base64.b64encode(ciphertext[-16:]).decode("utf-8"), "iv": base64.b64encode(nonce).decode("utf-8"), "encrypted_key": base64.b64encode(encrypted_key).decode("utf-8")}
    def decrypt(self, envelope: dict[str, str], private_key_pem: str) -> dict[str, Any]:
        nonce = base64.b64decode(envelope["iv"])
        ciphertext = base64.b64decode(envelope["encrypted_vote"]) + base64.b64decode(envelope["tag"])
        encrypted_key = base64.b64decode(envelope["encrypted_key"])
        private_key = self.load_private_key(private_key_pem)
        aes_key = private_key.decrypt(encrypted_key, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
        plaintext = AESGCM(aes_key).decrypt(nonce, ciphertext, None)
        return json.loads(plaintext.decode("utf-8"))
    def sign(self, payload: bytes, private_key_pem: str) -> str:
        private_key = self.load_private_key(private_key_pem)
        signature = private_key.sign(payload, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
        return base64.b64encode(signature).decode("utf-8")
    def verify(self, payload: bytes, signature: str, public_key_pem: str) -> bool:
        public_key = self.load_public_key(public_key_pem)
        try:
            public_key.verify(base64.b64decode(signature), payload, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
            return True
        except Exception:
            return False