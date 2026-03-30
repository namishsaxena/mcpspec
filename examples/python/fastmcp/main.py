"""Task Manager MCP server — FastMCP example with mcpspec docs.

Demonstrates route injection: McpSpec auto-registers /docs and /mcpspec.yaml
on the FastMCP server via custom_route(). Auth middleware protects /mcp only.
"""

from __future__ import annotations

import os

import uvicorn
from starlette.responses import JSONResponse

from auth import API_TOKEN, extract_bearer_token, verify_token
from mcpspec_dev import McpSpec
from server import mcp

spec = McpSpec(
    mcp,
    info={
        "title": "Task Manager",
        "description": (
            "A simple task management MCP server for demonstration.\n"
            "Supports creating, reading, updating, and deleting tasks\n"
            "with status tracking and priority levels."
        ),
        "version": "1.0.0",
        "repository": "https://github.com/namishsaxena/mcpspec",
        "license": "MIT",
        "authors": [{"name": "Namish Saxena", "url": "https://mcpspec.dev"}],
    },
    transport=[
        {
            "type": "streamable-http",
            "url": "/mcp",
            "description": (
                "Primary HTTP endpoint for browser and remote clients"
            ),
            "auth": {
                "type": "bearer",
                "description": (
                    "Set API_TOKEN env var or use the default demo token"
                ),
            },
        },
        {
            "type": "stdio",
            "command": "python -m examples.python.fastmcp.main",
            "description": (
                "Local stdio transport for CLI and desktop clients"
            ),
        },
    ],
    groups={
        "Tasks": [
            "create_task",
            "get_task",
            "list_tasks",
            "update_task",
            "delete_task",
        ],
        "Analytics": ["get_task_summary"],
    },
    examples={
        "create_task": [
            {
                "title": "Create a simple task",
                "input": {
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread",
                },
                "description": (
                    "Creates a new task with default medium priority"
                ),
            },
            {
                "title": "Create a high-priority task",
                "input": {
                    "title": "Fix production bug",
                    "description": (
                        "Users seeing 500 errors on /api/checkout"
                    ),
                    "priority": "high",
                },
                "description": "Creates an urgent task with high priority",
            },
        ],
        "list_tasks": [
            {
                "title": "List in-progress tasks",
                "input": {"status": "in_progress", "limit": 10},
                "description": (
                    "Returns up to 10 tasks that are currently in progress"
                ),
            },
        ],
    },
)

# McpSpec injected /docs and /mcpspec.yaml via custom_route().
# Get the Starlette ASGI app with all routes including /mcp.
_inner_app = mcp.streamable_http_app()

PORT = int(os.environ.get("PORT", "3000"))


async def app(scope, receive, send):
    """ASGI wrapper that enforces bearer auth on /mcp only."""
    if scope["type"] == "http" and scope["path"] == "/mcp":
        headers = dict(scope.get("headers", []))
        auth_header = headers.get(b"authorization", b"").decode()
        token = extract_bearer_token(auth_header)
        if not token or not verify_token(token):
            response = JSONResponse(
                {"error": "Bearer token required"},
                status_code=401,
                headers={"WWW-Authenticate": 'Bearer realm="mcp"'},
            )
            await response(scope, receive, send)
            return
    await _inner_app(scope, receive, send)


if __name__ == "__main__":
    print(f"Task Manager MCP server running at http://localhost:{PORT}")
    print(f"  Docs:  http://localhost:{PORT}/docs          (public)")
    print(f"  Spec:  http://localhost:{PORT}/mcpspec.yaml   (public)")
    print(f"  MCP:   http://localhost:{PORT}/mcp            (bearer auth)")
    print()
    if API_TOKEN == "mcpspec-demo-token":
        print(f"  Auth:  Authorization: Bearer {API_TOKEN}")
    else:
        print("  Auth:  Authorization: Bearer <redacted>")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
