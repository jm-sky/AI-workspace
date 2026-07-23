"""Agent routing strategies (MVP dec. #9 — explicit first)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

RoutingReason = Literal["explicit", "session", "default"]


@dataclass(frozen=True, slots=True)
class RoutingDecision:
    key: str
    reason: RoutingReason


class ExplicitAgentRouter:
    """Resolve agent key from request, then session, then tenant default.

    When a session already exists, its ``agent_key`` wins (locked for the conversation).
    Definition loading is left to the caller (DB / registry).
    """

    def resolve_key(
        self,
        *,
        explicit_key: str | None,
        session_key: str | None,
        default_key: str,
    ) -> RoutingDecision:
        if session_key:
            return RoutingDecision(key=session_key, reason="session")
        if explicit_key:
            return RoutingDecision(key=explicit_key, reason="explicit")
        return RoutingDecision(key=default_key, reason="default")
