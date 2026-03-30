"""Task Manager MCP server — native Server API example with mcpspec docs.

Demonstrates create_app() for low-level Server (no route injection).
Combines McpSpec doc routes with StreamableHTTP transport and auth.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.types import ASGIApp, Receive, Scope, Send

from auth import API_TOKEN, extract_bearer_token, verify_token
from mcpspec_dev import McpSpec
from server import server

spec = McpSpec(
    server,
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
            "command": "python -m examples.python.native.main",
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

# StreamableHTTP session manager bridges the low-level Server to HTTP
session_manager = StreamableHTTPSessionManager(app=server)


class _McpTransportApp:
    """ASGI app that delegates to the StreamableHTTP session manager."""

    def __init__(self, sm: StreamableHTTPSessionManager) -> None:
        self._sm = sm

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        await self._sm.handle_request(scope, receive, send)


mcp_transport = _McpTransportApp(session_manager)


@asynccontextmanager
async def lifespan(_app: Starlette) -> AsyncIterator[None]:
    """Manage StreamableHTTP session manager lifecycle."""
    async with session_manager.run():
        yield


# Combine McpSpec doc routes + MCP transport into one Starlette app.
# Since Server (not FastMCP) is used, McpSpec doesn't inject routes —
# we wire them manually via the spec's handler methods.
_starlette_app = Starlette(
    routes=[
        Route("/docs", spec._handle_docs, methods=["GET"]),
        Route("/mcpspec.yaml", spec._handle_yaml, methods=["GET"]),
        Route("/mcp", mcp_transport),
    ],
    lifespan=lifespan,
)

PORT = int(os.environ.get("PORT", "3001"))


async def app(scope: Scope, receive: Receive, send: Send) -> None:
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
    await _starlette_app(scope, receive, send)


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
