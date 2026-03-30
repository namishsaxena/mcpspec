"""Task Manager MCP server — native Server API example.

Same functionality as the FastMCP example, using the low-level Server API
with explicit handler registration and manual JSON Schema definitions.
"""

from __future__ import annotations

import json
from typing import Any

from mcp.server import Server
from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptMessage,
    Resource,
    TextContent,
    TextResourceContents,
    Tool,
)
from pydantic import AnyUrl

from tools import HANDLERS, TOOLS, tasks

server = Server("task-manager")


# ---------------------------------------------------------------------------
# Server handler registration
# ---------------------------------------------------------------------------


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return TOOLS


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[TextContent]:
    handler = HANDLERS.get(name)
    if not handler:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
    return handler(arguments or {})


@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    return [
        Resource(
            uri=AnyUrl("tasks://summary"),
            name="task-summary",
            mimeType="application/json",
        )
    ]


@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> list[TextResourceContents]:
    if str(uri) == "tasks://summary":
        all_tasks = list(tasks.values())
        return [
            TextResourceContents(
                uri=uri,
                text=json.dumps({
                    "total": len(all_tasks),
                    "byStatus": {
                        s: sum(1 for t in all_tasks if t["status"] == s)
                        for s in ("todo", "in_progress", "done")
                    },
                }),
                mimeType="application/json",
            )
        ]
    msg = f"Resource not found: {uri}"
    raise ValueError(msg)


@server.list_prompts()
async def handle_list_prompts() -> list[Prompt]:
    return [
        Prompt(
            name="task_report",
            description=(
                "Generate a task status report for the current sprint"
            ),
        )
    ]


@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> GetPromptResult:
    if name != "task_report":
        msg = f"Prompt not found: {name}"
        raise ValueError(msg)
    all_tasks = list(tasks.values())
    text = (
        "Generate a concise status report for these tasks:\n\n"
        + json.dumps(all_tasks, indent=2)
        + "\n\nInclude: summary stats, blockers, and next steps."
    )
    return GetPromptResult(
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=text),
            )
        ]
    )
