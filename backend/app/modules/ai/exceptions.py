"""AI-specific exceptions."""


class AIError(Exception):
    """Base exception for AI module errors."""

    pass


class TokenValidationError(AIError):
    """Raised when API token validation fails."""

    pass


class OpenRouterError(AIError):
    """Raised when OpenRouter API returns an error."""

    pass


class CacheError(AIError):
    """Raised when cache operations fail."""

    pass


class StructuredOutputParsingError(AIError):
    """Raised when AI structured output cannot be parsed."""

    pass


class ModelNotAvailableError(AIError):
    """Raised when requested model is not available."""

    pass


class AdminRequiredError(AIError):
    """Raised when non-admin user tries to access AI features."""

    pass


class EncryptionError(AIError):
    """Raised when token encryption/decryption fails."""

    pass
