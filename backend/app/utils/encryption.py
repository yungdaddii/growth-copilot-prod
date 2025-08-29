"""
Encryption utilities for storing sensitive data like OAuth tokens.
"""

import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from app.core.config import settings


def get_encryption_key() -> bytes:
    """Generate encryption key from SECRET_KEY."""
    # Use SECRET_KEY as the base for encryption
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'growth-copilot-salt',  # In production, use a random salt
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(settings.SECRET_KEY.encode()))
    return key


def encrypt_data(data: str) -> str:
    """Encrypt sensitive data."""
    f = Fernet(get_encryption_key())
    encrypted = f.encrypt(data.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data."""
    f = Fernet(get_encryption_key())
    decoded = base64.urlsafe_b64decode(encrypted_data.encode())
    decrypted = f.decrypt(decoded)
    return decrypted.decode()