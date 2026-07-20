"""Tool search: TF-IDF discovery + meta-tool to activate deferred tools (issue 022)."""

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any

from app.core.config import settings
from app.modules.agent.tools.base import (
    AgentTool,
    AgentToolDefinition,
    AgentToolRegistry,
)


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def _idf(term: str, docs: list[list[str]]) -> float:
    df = sum(1 for d in docs if term in d)
    if df == 0:
        return 0.0
    return math.log((len(docs) + 1) / (df + 1))


def _tfidf_score(
    query_tokens: list[str], doc_tokens: list[str], idf_map: dict[str, float]
) -> float:
    doc_counts = Counter(doc_tokens)
    doc_len = max(len(doc_tokens), 1)
    score = 0.0
    for term in query_tokens:
        tf = doc_counts.get(term, 0) / doc_len
        score += tf * idf_map.get(term, 0.0)
    return score


def search_tools(
    tools: list[dict[str, Any]],
    query: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Return top_k tools matching the query (in-memory TF-IDF).

    Empty / degenerate queries fall back to the first top_k tools.
    """
    if not tools or not query.strip():
        return tools[:top_k]

    query_tokens = _tokenize(query)
    if not query_tokens:
        return tools[:top_k]

    docs: list[list[str]] = []
    for tool in tools:
        fn = tool.get("function", {})
        name = fn.get("name", "")
        desc = fn.get("description") or ""
        docs.append(_tokenize(f"{name} {desc}"))

    idf_map = {term: _idf(term, docs) for term in set(query_tokens)}

    scored = [
        (i, _tfidf_score(query_tokens, doc_tokens, idf_map))
        for i, doc_tokens in enumerate(docs)
    ]
    scored.sort(key=lambda x: x[1], reverse=True)

    result = [tools[i] for i, _score in scored[:top_k]]
    return result if result else tools[:top_k]


class ToolSearchTool(AgentTool):
    """Meta-tool: search deferred tools and activate matches for subsequent loop turns."""

    def __init__(
        self,
        *,
        registry: AgentToolRegistry,
        top_k: int | None = None,
    ):
        self.registry = registry
        self.top_k = top_k if top_k is not None else settings.ai.tool_search_top_k

    @property
    def definition(self) -> AgentToolDefinition:
        return AgentToolDefinition(
            name="tool_search",
            description=(
                "Search the deferred tool catalog by natural language and load matching "
                "tools into this turn. Call when you need a capability that is not in "
                "the currently available tools list."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "What capability you need (e.g. 'search github repositories')"
                        ),
                    },
                },
                "required": ["query"],
            },
        )

    async def execute(self, arguments: dict[str, Any]) -> dict[str, Any]:
        query = str(arguments.get("query", "")).strip()
        if not query:
            return {"error": "query is required"}

        deferred = self.registry.deferred_openai_tools()
        if not deferred:
            return {
                "activated": [],
                "tools": [],
                "message": "No deferred tools available",
            }

        selected = search_tools(deferred, query, top_k=self.top_k)
        names = [
            t.get("function", {}).get("name", "")
            for t in selected
            if t.get("function", {}).get("name")
        ]
        activated = self.registry.activate(names)

        tools_info: list[dict[str, str]] = []
        for name in activated:
            tool = self.registry.get(name)
            if tool is None:
                continue
            desc = (tool.definition.description or "").strip().split("\n")[0]
            tools_info.append({"name": name, "description": desc})

        return {
            "activated": activated,
            "tools": tools_info,
            "query": query,
        }
