"""Agent module exceptions."""


class AgentError(Exception):
    """Base agent error."""


class AgentNotConfiguredError(AgentError):
    """Agent or OpenRouter is not configured."""


class AgentToolsDisabledError(AgentError):
    """Tools are disabled for this workspace."""


class AgentMaxStepsExceededError(AgentError):
    """Agent exceeded maximum tool-calling steps."""


class AgentToolError(AgentError):
    """Tool execution failed."""
