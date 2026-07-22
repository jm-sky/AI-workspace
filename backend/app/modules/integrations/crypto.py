"""Encryption utilities for integration OAuth tokens."""

import base64

from cryptography.fernet import Fernet

from app.core.config import settings
from app.modules.integrations.exceptions import IntegrationEncryptionError


def _get_cipher() -> Fernet:
    key = settings.integrations.token_encryption_key or settings.ai.token_encryption_key
    if not key:
        raise IntegrationEncryptionError("INTEGRATION_TOKEN_ENCRYPTION_KEY or AI_TOKEN_ENCRYPTION_KEY not configured")
    try:
        return Fernet(key)
    except Exception as exc:
        raise IntegrationEncryptionError(f"Invalid encryption key: {exc}") from exc


def encrypt_integration_token(token: str) -> str:
    try:
        cipher = _get_cipher()
        encrypted_bytes = cipher.encrypt(token.encode())
        return base64.b64encode(encrypted_bytes).decode()
    except IntegrationEncryptionError:
        raise
    except Exception as exc:
        raise IntegrationEncryptionError(f"Token encryption failed: {exc}") from exc


def decrypt_integration_token(encrypted_token: str) -> str:
    try:
        cipher = _get_cipher()
        encrypted_bytes = base64.b64decode(encrypted_token)
        return cipher.decrypt(encrypted_bytes).decode()
    except IntegrationEncryptionError:
        raise
    except Exception as exc:
        raise IntegrationEncryptionError(f"Token decryption failed: {exc}") from exc
