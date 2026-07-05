"""Token encryption utilities using Fernet symmetric encryption."""

import base64

from cryptography.fernet import Fernet

from app.core.config import settings
from app.modules.ai.exceptions import EncryptionError


def get_cipher() -> Fernet:
    """Get Fernet cipher from settings.

    Returns:
        Fernet cipher instance

    Raises:
        EncryptionError: If encryption key is not configured
    """
    key = settings.ai.token_encryption_key
    if not key:
        raise EncryptionError("AI_TOKEN_ENCRYPTION_KEY not configured in settings")

    # Fernet accepts both string (base64) and bytes automatically
    # - String from .env: base64-encoded key (e.g., "mAAv4ghCKiD80hSWadVIUdEUzVn6FF7MeJgSQF1Pnzs=")
    # - Bytes: raw bytes from programmatic usage
    try:
        return Fernet(key)
    except Exception as e:
        raise EncryptionError(f"Invalid encryption key: {e}") from e


def encrypt_token(token: str) -> str:
    """Encrypt an API token using Fernet.

    Args:
        token: Plain text API token

    Returns:
        Base64-encoded encrypted token

    Raises:
        EncryptionError: If encryption fails
    """
    try:
        cipher = get_cipher()
        encrypted_bytes = cipher.encrypt(token.encode())
        return base64.b64encode(encrypted_bytes).decode()
    except Exception as e:
        raise EncryptionError(f"Token encryption failed: {e}") from e


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt an encrypted API token.

    Args:
        encrypted_token: Base64-encoded encrypted token

    Returns:
        Plain text API token

    Raises:
        EncryptionError: If decryption fails
    """
    try:
        cipher = get_cipher()
        encrypted_bytes = base64.b64decode(encrypted_token)
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        return decrypted_bytes.decode()
    except Exception as e:
        raise EncryptionError(f"Token decryption failed: {e}") from e
