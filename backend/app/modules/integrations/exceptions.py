"""Exceptions for integration token module."""


class IntegrationError(Exception):
    """Base integration error."""


class IntegrationEncryptionError(IntegrationError):
    """Encryption or decryption failed."""


class IntegrationTokenNotFoundError(IntegrationError):
    """No token stored for user/provider."""


class IntegrationTokenExpiredError(IntegrationError):
    """Token expired and could not be refreshed."""


class IntegrationOAuthStateError(IntegrationError):
    """Invalid or expired OAuth state."""


class IntegrationPermissionError(IntegrationError):
    """Caller lacks permission for this integration action."""
