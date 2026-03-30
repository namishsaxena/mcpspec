"""Tool definitions and handlers for the native Server example.

Contains the in-memory task store, JSON Schema tool definitions,
and handler functions for all 6 tools.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from mcp.types import TextContent, Tool, ToolAnnotations

# ---------------------------------------------------------------------------
# In-memory task store
# ---------------------------------------------------------------------------

tasks: dict[str, dict[str, Any]] = {}
_next_id = 1


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Shared annotation and schema constants
# ---------------------------------------------------------------------------

_READ_ONLY = ToolAnnotations(
    readOnlyHint=True, idempotentHint=True, openWorldHint=False
)
_WRITE = ToolAnnotations(
    readOnlyHint=False, idempotentHint=False, openWorldHint=False
)
_WRITE_IDEMPOTENT = ToolAnnotations(
    readOnlyHint=False, idempotentHint=True, openWorldHint=False
)
_DESTRUCTIVE = ToolAnnotations(
    destructiveHint=True, idempotentHint=True, openWorldHint=False
)

_STATUS_ENUM = {"type": "string", "enum": ["todo", "in_progress", "done"]}
_PRIORITY_ENUM = {"type": "string", "enum": ["low", "medium", "high"]}


# ---------------------------------------------------------------------------
# Tool definitions
# ---------------------------------------------------------------------------

TOOLS = [
    Tool(
        name="create_task",
        description=(
            "Create a new task with a title, optional description, "
            "and priority"
        ),
        annotations=_WRITE,
        inputSchema={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Task title"},
                "description": {
                    "type": "string",
                    "description": "Detailed task description",
                },
                "priority": {
                    **_PRIORITY_ENUM,
                    "description": (
                        "Task priority level (defaults to medium)"
                    ),
                },
            },
            "required": ["title"],
        },
    ),
    Tool(
        name="get_task",
        description="Retrieve a single task by its ID",
        annotations=_READ_ONLY,
        inputSchema={
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Task ID"},
            },
            "required": ["id"],
        },
    ),
    Tool(
        name="list_tasks",
        description=(
            "List tasks with optional filtering by status and priority"
        ),
        annotations=_READ_ONLY,
        inputSchema={
            "type": "object",
            "properties": {
                "status": {
                    **_STATUS_ENUM,
                    "description": "Filter by task status",
                },
                "priority": {
                    **_PRIORITY_ENUM,
                    "description": "Filter by priority level",
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "description": (
                        "Maximum number of tasks to return "
                        "(default: 25, max: 100)"
                    ),
                },
            },
        },
    ),
    Tool(
        name="update_task",
        description="Update fields on an existing task",
        annotations=_WRITE_IDEMPOTENT,
        inputSchema={
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Task ID"},
                "title": {"type": "string", "description": "New title"},
                "description": {
                    "type": "string",
                    "description": "New description",
                },
                "status": {**_STATUS_ENUM, "description": "New status"},
                "priority": {
                    **_PRIORITY_ENUM,
                    "description": "New priority",
                },
            },
            "required": ["id"],
        },
    ),
    Tool(
        name="delete_task",
        description="Permanently delete a task by ID",
        annotations=_DESTRUCTIVE,
        inputSchema={
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Task ID to delete",
                },
            },
            "required": ["id"],
        },
    ),
    Tool(
        name="get_task_summary",
        description=(
            "Get aggregate task counts grouped by status and priority"
        ),
        annotations=_READ_ONLY,
        inputSchema={"type": "object", "properties": {}},
    ),
]


# ---------------------------------------------------------------------------
# Tool handler implementations
# ---------------------------------------------------------------------------


def _create_task(args: dict[str, Any]) -> list[TextContent]:
    global _next_id
    task_id = str(_next_id)
    _next_id += 1
    task = {
        "id": task_id,
        "title": args["title"],
        "description": args.get("description", ""),
        "status": "todo",
        "priority": args.get("priority", "medium"),
        "createdAt": _now(),
        "updatedAt": _now(),
    }
    tasks[task_id] = task
    return [TextContent(type="text", text=json.dumps(task, indent=2))]


def _get_task(args: dict[str, Any]) -> list[TextContent]:
    task = tasks.get(args["id"])
    if not task:
        return [TextContent(type="text", text=f"Task {args['id']} not found")]
    return [TextContent(type="text", text=json.dumps(task, indent=2))]


def _list_tasks(args: dict[str, Any]) -> list[TextContent]:
    result = list(tasks.values())
    if args.get("status"):
        result = [t for t in result if t["status"] == args["status"]]
    if args.get("priority"):
        result = [t for t in result if t["priority"] == args["priority"]]
    return [
        TextContent(
            type="text",
            text=json.dumps(result[: args.get("limit") or 25], indent=2),
        )
    ]


def _update_task(args: dict[str, Any]) -> list[TextContent]:
    task = tasks.get(args["id"])
    if not task:
        return [TextContent(type="text", text=f"Task {args['id']} not found")]
    for field in ("title", "description", "status", "priority"):
        if args.get(field) is not None:
            task[field] = args[field]
    task["updatedAt"] = _now()
    return [TextContent(type="text", text=json.dumps(task, indent=2))]


def _delete_task(args: dict[str, Any]) -> list[TextContent]:
    existed = tasks.pop(args["id"], None)
    msg = (
        f"Task {args['id']} deleted successfully"
        if existed
        else f"Task {args['id']} not found"
    )
    return [TextContent(type="text", text=msg)]


def _get_task_summary(_args: dict[str, Any]) -> list[TextContent]:
    all_tasks = list(tasks.values())
    summary = {
        "total": len(all_tasks),
        "byStatus": {
            s: sum(1 for t in all_tasks if t["status"] == s)
            for s in ("todo", "in_progress", "done")
        },
        "byPriority": {
            p: sum(1 for t in all_tasks if t["priority"] == p)
            for p in ("low", "medium", "high")
        },
    }
    return [TextContent(type="text", text=json.dumps(summary, indent=2))]


HANDLERS: dict[str, Any] = {
    "create_task": _create_task,
    "get_task": _get_task,
    "list_tasks": _list_tasks,
    "update_task": _update_task,
    "delete_task": _delete_task,
    "get_task_summary": _get_task_summary,
}
