"""Validators for gear module - markdown link security and sanitization."""

import re
from urllib.parse import urlparse

# Security configuration
MAX_LINK_LENGTH = 2048
MAX_MARKDOWN_LENGTH = 50000
ALLOWED_PROTOCOLS = ["http", "https"]
BLOCKED_PROTOCOLS = [
    "javascript",
    "data",
    "vbscript",
    "file",
    "about",
    "jar",
    "chrome",
    "chrome-extension",
]


def is_protocol_allowed(protocol: str) -> bool:
    """Check if a protocol is allowed."""
    return protocol.lower() in ALLOWED_PROTOCOLS


def is_protocol_blocked(protocol: str) -> bool:
    """Check if a protocol is blocked."""
    return any(protocol.lower().startswith(blocked) for blocked in BLOCKED_PROTOCOLS)


def validate_link_length(url: str, max_length: int = MAX_LINK_LENGTH) -> bool:
    """Validate that a link URL is within allowed length."""
    return len(url) <= max_length


def is_dangerous_protocol(url: str) -> bool:
    """Check if a URL uses a dangerous protocol."""
    try:
        parsed = urlparse(url)
        protocol = parsed.scheme.lower()
        return is_protocol_blocked(protocol)
    except Exception:
        # If parsing fails, check if URL starts with blocked protocol
        return any(
            url.lower().startswith(f"{blocked}:") for blocked in BLOCKED_PROTOCOLS
        )


def sanitize_markdown_content(
    content: str, max_length: int = MAX_MARKDOWN_LENGTH
) -> str:
    """Sanitize markdown content by removing dangerous links and validating length.

    Args:
        content: Markdown content to sanitize
        max_length: Maximum allowed length for content

    Returns:
        Sanitized markdown content

    Raises:
        ValueError: If content exceeds max_length
    """
    if len(content) > max_length:
        raise ValueError(
            f"Markdown content exceeds maximum length of {max_length} characters"
        )

    # Remove dangerous protocol links using regex
    # Match URLs with dangerous protocols
    dangerous_pattern = re.compile(
        r"\b("
        + "|".join(re.escape(proto) + ":" for proto in BLOCKED_PROTOCOLS)
        + r")[^\s]*",
        re.IGNORECASE,
    )

    sanitized = dangerous_pattern.sub("", content)
    return sanitized


def sanitize_link(url: str) -> str | None:
    """Sanitize a link by removing dangerous protocols.

    Args:
        url: URL to sanitize

    Returns:
        Sanitized URL or None if protocol is blocked
    """
    if is_dangerous_protocol(url):
        return None

    try:
        parsed = urlparse(url)
        if not is_protocol_allowed(parsed.scheme):
            return None
        return url
    except Exception:
        # If parsing fails, return None for safety
        return None


def validate_markdown_link(url: str, max_length: int = MAX_LINK_LENGTH) -> bool:
    """Validate a markdown link.

    Args:
        url: URL to validate
        max_length: Maximum allowed length for URL

    Returns:
        True if link is valid, False otherwise
    """
    if not validate_link_length(url, max_length):
        return False

    if is_dangerous_protocol(url):
        return False

    return True
