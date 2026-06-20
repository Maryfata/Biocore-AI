"""Encryption utilities for HIPAA compliance"""
from cryptography.fernet import Fernet
from api.config import settings
import hashlib
import base64


class MedicalEncryption:
    def __init__(self):
        key = settings.ENCRYPTION_KEY[:32].ljust(32)
        key = hashlib.sha256(key.encode()).digest()
        key_b64 = base64.urlsafe_b64encode(key)
        self.cipher = Fernet(key_b64)

    def encrypt(self, plaintext: str) -> bytes:
        return self.cipher.encrypt(plaintext.encode())

    def decrypt(self, ciphertext: bytes) -> str:
        return self.cipher.decrypt(ciphertext).decode()


encryption = MedicalEncryption()
