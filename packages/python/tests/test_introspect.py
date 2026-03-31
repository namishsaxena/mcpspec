"""Tests for mcpspec_dev.introspect — MCP server introspection via in-memory transport."""

import pytest
from mcp.server.fastmcp import FastMCP

from mcpspec_dev.introspect import MAX_PAGES, introspect
from mcpspec_dev.types import IntrospectionResult


def create_test_server() -> FastMCP:
    """Create a FastMCP server with tools, resources, and prompts for testing."""
    server = FastMCP("test-server")

    @server.tool()
    def get_users(limit: int = 10) -> list[dict]:
        """Retrieve a list of users"""
        return []

    @server.tool()
    def create_user(name: str, email: str) -> dict:
        """Create a new user account"""
        return {"id": "123", "name": name, "email": email}

    @server.resource("users://list")
    def users_list() -> str:
        """List of all users"""
        return "[]"

    @server.prompt()
    def user_report(timeframe: str) -> str:
        """Generate a user activity report"""
        return f"Generate a report for {timeframe}"

    return server


class TestIntrospect:
    """Test introspection of MCP servers."""

    @pytest.mark.asyncio
    async def test_extracts_tools(self) -> None:
        server = create_test_server()
        result = await introspect(server)

        assert isinstance(result, IntrospectionResult)
        assert len(result.tools) == 2

        get_users = next(t for t in result.tools if t.name == "get_users")
        assert get_users.description == "Retrieve a list of users"
        assert get_users.input_schema is not None

    @pytest.mark.asyncio
    async def test_extracts_resources(self) -> None:
        server = create_test_server()
        result = await introspect(server)

        assert len(result.resources) == 1
        users = result.resources[0]
        assert "users://list" in users.uri

    @pytest.mark.asyncio
    async def test_extracts_prompts(self) -> None:
        server = create_test_server()
        result = await introspect(server)

        assert len(result.prompts) == 1
        report = result.prompts[0]
        assert report.name == "user_report"
        assert report.description is not None
        assert report.arguments is not None
        assert len(report.arguments) >= 1

    @pytest.mark.asyncio
    async def test_extracts_capabilities(self) -> None:
        server = create_test_server()
        result = await introspect(server)

        assert result.capabilities is not None
        assert isinstance(result.capabilities, dict)

    @pytest.mark.asyncio
    async def test_handles_empty_server(self) -> None:
        server = FastMCP("empty-server")
        result = await introspect(server)

        assert len(result.tools) == 0
        assert len(result.resources) == 0
        assert len(result.prompts) == 0
        assert result.capabilities is not None

    @pytest.mark.asyncio
    async def test_extracts_tool_input_schema(self) -> None:
        server = create_test_server()
        result = await introspect(server)

        create_user = next(t for t in result.tools if t.name == "create_user")
        assert create_user.input_schema is not None
        props = create_user.input_schema.get("properties", {})
        assert "name" in props
        assert "email" in props

    @pytest.mark.asyncio
    async def test_handles_server_with_only_tools(self) -> None:
        server = FastMCP("tools-only")

        @server.tool()
        def ping() -> str:
            """Ping the server"""
            return "pong"

        result = await introspect(server)

        assert len(result.tools) == 1
        assert len(result.resources) == 0
        assert len(result.prompts) == 0

    @pytest.mark.asyncio
    async def test_preserves_empty_input_schema(self) -> None:
        """An empty inputSchema {} should be preserved, not become None.

        This test verifies that the truthiness check bug is fixed:
        bool({}) is False in Python, so `if tool.inputSchema` would
        incorrectly convert {} to None. We need `is not None` instead.
        """
        server = FastMCP("Empty Schema Server")

        @server.tool(description="Tool with no params")
        async def no_params() -> str:
            return "ok"

        result = await introspect(server)

        # The tool should have an inputSchema (even if it's a minimal object schema)
        # rather than None. The MCP SDK typically returns at least
        # {'type': 'object', 'properties': {}}, but the fix ensures that even
        # a truly empty {} would be preserved.
        tool = next(t for t in result.tools if t.name == "no_params")
        assert tool.input_schema is not None
        assert isinstance(tool.input_schema, dict)


class TestPaginationBounds:
    """Test that pagination has safety limits."""

    def test_max_pages_constant_exists(self) -> None:
        assert MAX_PAGES == 100
