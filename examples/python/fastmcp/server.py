"""Task Manager MCP server — FastMCP example.

Implements 6 tools, 1 resource, and 1 prompt for task management.
Mirrors the TypeScript example in examples/typescript/.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Annotated, Any, Literal

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

mcp = FastMCP("task-manager")

# ---------------------------------------------------------------------------
# In-memory task store
# ---------------------------------------------------------------------------

tasks: dict[str, dict[str, Any]] = {}
_next_id = 1


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Tools — Tasks group
# ---------------------------------------------------------------------------


@mcp.tool(
    description="Create a new task with a title, optional description, and priority",
    annotations=ToolAnnotations(
        readOnlyHint=False, idempotentHint=False, openWorldHint=False
    ),
)
async def create_task(
    title: Annotated[str, Field(description="Task title")],
    description: Annotated[str, Field(description="Detailed task description")] = "",
    priority: Annotated[
        Literal["low", "medium", "high"],
        Field(description="Task priority level (defaults to medium)"),
    ] = "medium",
) -> str:
    global _next_id
    task_id = str(_next_id)
    _next_id += 1
    task = {
        "id": task_id,
        "title": title,
        "description": description,
        "status": "todo",
        "priority": priority,
        "createdAt": _now(),
        "updatedAt": _now(),
    }
    tasks[task_id] = task
    return json.dumps(task, indent=2)


@mcp.tool(
    description="Retrieve a single task by its ID",
    annotations=ToolAnnotations(
        readOnlyHint=True, idempotentHint=True, openWorldHint=False
    ),
)
async def get_task(
    id: Annotated[str, Field(description="Task ID")],
) -> str:
    task = tasks.get(id)
    if not task:
        raise ValueError(f"Task {id} not found")
    return json.dumps(task, indent=2)


@mcp.tool(
    description="List tasks with optional filtering by status and priority",
    annotations=ToolAnnotations(
        readOnlyHint=True, idempotentHint=True, openWorldHint=False
    ),
)
async def list_tasks(
    status: Annotated[
        Literal["todo", "in_progress", "done"] | None,
        Field(description="Filter by task status"),
    ] = None,
    priority: Annotated[
        Literal["low", "medium", "high"] | None,
        Field(description="Filter by priority level"),
    ] = None,
    limit: Annotated[
        int | None,
        Field(
            description="Maximum number of tasks to return (default: 25, max: 100)",
            ge=1,
            le=100,
        ),
    ] = None,
) -> str:
    result = list(tasks.values())
    if status:
        result = [t for t in result if t["status"] == status]
    if priority:
        result = [t for t in result if t["priority"] == priority]
    return json.dumps(result[: limit or 25], indent=2)


@mcp.tool(
    description="Update fields on an existing task",
    annotations=ToolAnnotations(
        readOnlyHint=False, idempotentHint=True, openWorldHint=False
    ),
)
async def update_task(
    id: Annotated[str, Field(description="Task ID")],
    title: Annotated[str | None, Field(description="New title")] = None,
    description: Annotated[str | None, Field(description="New description")] = None,
    status: Annotated[
        Literal["todo", "in_progress", "done"] | None,
        Field(description="New status"),
    ] = None,
    priority: Annotated[
        Literal["low", "medium", "high"] | None,
        Field(description="New priority"),
    ] = None,
) -> str:
    task = tasks.get(id)
    if not task:
        raise ValueError(f"Task {id} not found")
    if title is not None:
        task["title"] = title
    if description is not None:
        task["description"] = description
    if status is not None:
        task["status"] = status
    if priority is not None:
        task["priority"] = priority
    task["updatedAt"] = _now()
    return json.dumps(task, indent=2)


@mcp.tool(
    description="Permanently delete a task by ID",
    annotations=ToolAnnotations(
        destructiveHint=True, idempotentHint=True, openWorldHint=False
    ),
)
async def delete_task(
    id: Annotated[str, Field(description="Task ID to delete")],
) -> str:
    existed = tasks.pop(id, None)
    if existed:
        return f"Task {id} deleted successfully"
    return f"Task {id} not found"


# ---------------------------------------------------------------------------
# Tools — Analytics group
# ---------------------------------------------------------------------------


@mcp.tool(
    description="Get aggregate task counts grouped by status and priority",
    annotations=ToolAnnotations(
        readOnlyHint=True, idempotentHint=True, openWorldHint=False
    ),
)
async def get_task_summary() -> str:
    all_tasks = list(tasks.values())
    summary = {
        "total": len(all_tasks),
        "byStatus": {
            "todo": sum(1 for t in all_tasks if t["status"] == "todo"),
            "in_progress": sum(
                1 for t in all_tasks if t["status"] == "in_progress"
            ),
            "done": sum(1 for t in all_tasks if t["status"] == "done"),
        },
        "byPriority": {
            "low": sum(1 for t in all_tasks if t["priority"] == "low"),
            "medium": sum(1 for t in all_tasks if t["priority"] == "medium"),
            "high": sum(1 for t in all_tasks if t["priority"] == "high"),
        },
    }
    return json.dumps(summary, indent=2)


# ---------------------------------------------------------------------------
# Resource
# ---------------------------------------------------------------------------


@mcp.resource("tasks://summary", mime_type="application/json")
async def task_summary() -> str:
    all_tasks = list(tasks.values())
    return json.dumps({
        "total": len(all_tasks),
        "byStatus": {
            "todo": sum(1 for t in all_tasks if t["status"] == "todo"),
            "in_progress": sum(
                1 for t in all_tasks if t["status"] == "in_progress"
            ),
            "done": sum(1 for t in all_tasks if t["status"] == "done"),
        },
    })


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------


@mcp.prompt(description="Generate a task status report for the current sprint")
async def task_report() -> str:
    all_tasks = list(tasks.values())
    return (
        "Generate a concise status report for these tasks:\n\n"
        + json.dumps(all_tasks, indent=2)
        + "\n\nInclude: summary stats, blockers, and next steps."
    )
