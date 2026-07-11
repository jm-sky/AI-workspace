"""Exceptions for integration token module."""


class IntegrationError(Exception):
    """Base integration error."""


class IntegrationEncryptionError(IntegrationError):
    """Encryption or decryption failed."""


class IntegrationTokenNotFoundError(IntegrationError):
    """No token stored for user/provider."""


class IntegrationTokenExpiredError(IntegrationError):
    """Token expired and could not be refreshed."""


class IntegrationRefreshNotSupportedError(IntegrationError):
    """Provider cannot exchange a refresh token for a new access token."""


class IntegrationRefreshFailedError(IntegrationError):
    """Provider rejected the refresh token or was unreachable."""


class IntegrationOAuthStateError(IntegrationError):
    """Invalid or expired OAuth state."""


class IntegrationPermissionError(IntegrationError):
    """Caller lacks permission for this integration action."""
