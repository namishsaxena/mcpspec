"""Integration tests — full McpSpec flow with real MCP servers."""

import yaml
from mcp.server.fastmcp import FastMCP
from starlette.testclient import TestClient

from mcpspec_dev.mcpspec import McpSpec


def create_full_server() -> FastMCP:
    """Create a server with tools, resources, prompts — matches TypeScript example."""
    server = FastMCP("integration-test")

    @server.tool()
    def create_task(title: str, description: str = "", priority: str = "medium") -> dict:
        """Create a new task with a title, optional description, and priority"""
        return {"id": "1", "title": title}

    @server.tool()
    def get_task(id: str) -> dict:
        """Retrieve a single task by its ID"""
        return {"id": id}

    @server.tool()
    def list_tasks(status: str | None = None, limit: int = 25) -> list:
        """List tasks with optional filtering by status and priority"""
        return []

    @server.tool()
    def update_task(id: str, title: str | None = None) -> dict:
        """Update fields on an existing task"""
        return {"id": id}

    @server.tool()
    def delete_task(id: str) -> str:
        """Permanently delete a task by ID"""
        return f"Deleted {id}"

    @server.tool()
    def get_task_summary() -> dict:
        """Get aggregate task counts grouped by status and priority"""
        return {"total": 0}

    @server.resource("tasks://summary")
    def task_summary() -> str:
        """Task summary resource"""
        return '{"total": 0}'

    @server.prompt()
    def task_report() -> str:
        """Generate a task status report for the current sprint"""
        return "Generate a report"

    return server


class TestFullFlow:
    """End-to-end integration tests."""

    def test_docs_returns_html_with_all_tools(self) -> None:
        server = create_full_server()
        spec = McpSpec(
            server,
            info={
                "title": "Integration Test Server",
                "version": "1.0.0",
                "description": "E2E test",
            },
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
        )

        app = spec.create_app()
        client = TestClient(app)

        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Integration Test Server" in response.text
        for tool in [
            "create_task",
            "get_task",
            "list_tasks",
            "update_task",
            "delete_task",
            "get_task_summary",
        ]:
            assert tool in response.text

    def test_yaml_returns_full_spec(self) -> None:
        server = create_full_server()
        spec = McpSpec(
            server,
            info={"title": "Integration Test Server", "version": "1.0.0"},
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
        )

        app = spec.create_app()
        client = TestClient(app)

        response = client.get("/mcpspec.yaml")
        assert response.status_code == 200
        parsed = yaml.safe_load(response.text)

        assert parsed["mcpspec"] == "0.1.0"
        assert parsed["info"]["title"] == "Integration Test Server"
        assert len(parsed["tools"]) == 6
        assert len(parsed["resources"]) == 1
        assert len(parsed["prompts"]) == 1

        tool_groups = {t["name"]: t.get("group") for t in parsed["tools"]}
        assert tool_groups["create_task"] == "Tasks"
        assert tool_groups["get_task_summary"] == "Analytics"

    def test_exclude_filters_tools(self) -> None:
        server = create_full_server()
        spec = McpSpec(
            server,
            info={"title": "Filtered", "version": "1.0.0"},
            exclude=["delete_*", "get_task_summary"],
        )

        app = spec.create_app()
        client = TestClient(app)

        response = client.get("/mcpspec.yaml")
        parsed = yaml.safe_load(response.text)

        tool_names = [t["name"] for t in parsed["tools"]]
        assert "delete_task" not in tool_names
        assert "get_task_summary" not in tool_names
        assert "create_task" in tool_names

    def test_transport_metadata_in_spec(self) -> None:
        server = create_full_server()
        spec = McpSpec(
            server,
            info={"title": "Transport Test", "version": "1.0.0"},
            transport=[
                {
                    "type": "streamable-http",
                    "url": "/mcp",
                    "auth": {"type": "bearer"},
                }
            ],
        )

        app = spec.create_app()
        client = TestClient(app)

        response = client.get("/mcpspec.yaml")
        parsed = yaml.safe_load(response.text)

        assert "transport" in parsed
        assert parsed["transport"][0]["type"] == "streamable-http"
        assert parsed["transport"][0]["auth"]["type"] == "bearer"

    def test_examples_attached_to_tools(self) -> None:
        server = create_full_server()
        spec = McpSpec(
            server,
            info={"title": "Examples Test", "version": "1.0.0"},
            examples={
                "create_task": [
                    {
                        "title": "Simple task",
                        "input": {"title": "Test"},
                        "description": "A test",
                    }
                ],
            },
        )

        app = spec.create_app()
        client = TestClient(app)

        response = client.get("/mcpspec.yaml")
        parsed = yaml.safe_load(response.text)

        create_tool = next(t for t in parsed["tools"] if t["name"] == "create_task")
        assert "examples" in create_tool
        assert create_tool["examples"][0]["title"] == "Simple task"

    def test_base_path_routes(self) -> None:
        server = create_full_server()
        spec = McpSpec(
            server,
            info={"title": "Base Path", "version": "1.0.0"},
            base_path="/api/v2",
        )

        app = spec.create_app()
        client = TestClient(app)

        assert client.get("/api/v2/docs").status_code == 200
        assert client.get("/api/v2/mcpspec.yaml").status_code == 200

    def test_yaml_structural_validation(self) -> None:
        """Verify generated YAML has all required sections and fields."""
        server = create_full_server()
        spec = McpSpec(
            server,
            info={
                "title": "Validation Test",
                "version": "1.0.0",
                "description": "Full validation",
                "repository": "https://github.com/test/repo",
                "license": "MIT",
            },
        )

        app = spec.create_app()
        client = TestClient(app)

        response = client.get("/mcpspec.yaml")
        parsed = yaml.safe_load(response.text)

        # Top-level structure
        for key in ["mcpspec", "$schema", "info", "tools", "resources", "prompts"]:
            assert key in parsed

        # Info block
        for key in ["name", "version", "title"]:
            assert key in parsed["info"]

        # Tools have required fields
        for tool in parsed["tools"]:
            assert "name" in tool
            assert "description" in tool

        # Resources have required fields
        for resource in parsed["resources"]:
            assert "uri" in resource

        # Prompts have required fields
        for prompt in parsed["prompts"]:
            assert "name" in prompt
