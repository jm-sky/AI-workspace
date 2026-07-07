"""Memory scope and source types."""

from enum import StrEnum


class MemoryScope(StrEnum):
    """Who can see a memory entry."""

    SESSION = "session"
    USER = "user"
    AGENT = "agent"


class MemorySource(StrEnum):
    """How the memory was created."""

    USER = "user"
    AGENT = "agent"
    RUN = "run"
