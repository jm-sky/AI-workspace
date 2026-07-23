"""Gmail MCP tool definitions and execution (OpenAI-compatible schemas)."""

from typing import Any

from app.modules.mcp.gmail.client import GmailApiClient

GMAIL_MCP_TOOLS: list[dict[str, Any]] = [
    {
        "name": "gmail_search_messages",
        "description": (
            "Search Gmail messages with Gmail query syntax "
            "(e.g. 'from:alice@example.com newer_than:7d subject:invoice'). "
            "Returns message metadata (subject, from, date, snippet)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Gmail search query (same as Gmail search box)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 10, max 50)",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "gmail_list_messages",
        "description": (
            "List recent Gmail messages, optionally filtered by label "
            "(default INBOX). Prefer gmail_search_messages when a query is known."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "labelIds": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Gmail label IDs (default: [\"INBOX\"])",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results (default 15, max 50)",
                },
            },
        },
    },
    {
        "name": "gmail_get_message",
        "description": (
            "Get a single Gmail message by id, including plain-text body when available."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "messageId": {
                    "type": "string",
                    "description": "Gmail message id",
                },
            },
            "required": ["messageId"],
        },
    },
]


async def execute_gmail_tool(
    client: GmailApiClient,
    tool_name: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """Dispatch a Gmail MCP tool call."""
    if tool_name == "gmail_search_messages":
        query = str(arguments.get("query") or "").strip()
        if not query:
            return {"error": "query is required"}
        limit = int(arguments.get("limit") or 10)
        data = await client.list_messages(query=query, max_results=limit)
        return {
            "messages": data.get("messages") or [],
            "resultSizeEstimate": data.get("resultSizeEstimate"),
            "nextPageToken": data.get("nextPageToken"),
        }

    if tool_name == "gmail_list_messages":
        limit = int(arguments.get("limit") or 15)
        label_ids = arguments.get("labelIds")
        if not isinstance(label_ids, list) or not label_ids:
            label_ids = ["INBOX"]
        labels = [str(x) for x in label_ids]
        data = await client.list_messages(label_ids=labels, max_results=limit)
        return {
            "messages": data.get("messages") or [],
            "resultSizeEstimate": data.get("resultSizeEstimate"),
            "nextPageToken": data.get("nextPageToken"),
        }

    if tool_name == "gmail_get_message":
        message_id = str(arguments.get("messageId") or "").strip()
        if not message_id:
            return {"error": "messageId is required"}
        message = await client.get_message(message_id, format="full")
        return {"message": message}

    return {"error": f"Unknown Gmail tool: {tool_name}"}
