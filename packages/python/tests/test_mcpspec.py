"""Tests for mcpspec_dev.mcpspec — McpSpec class with route injection and create_app."""

import logging

import pytest
from mcp.server.fastmcp import FastMCP
from starlette.testclient import TestClient

from mcpspec_dev.mcpspec import McpSpec


def create_test_server() -> FastMCP:
    server = FastMCP("test-server")

    @server.tool()
    def greet(name: str) -> str:
        """Say hello to someone"""
        return f"Hello, {name}!"

    @server.tool()
    def add(a: int, b: int) -> int:
        """Add two numbers"""
        return a + b

    return server


class TestMcpSpecRouteInjection:
    """Test McpSpec with FastMCP route injection."""

    def test_injects_docs_and_yaml_routes(self) -> None:
        server = create_test_server()
        spec = McpSpec(server, info={"title": "Test", "version": "1.0.0"})

        app = spec.create_app()
        client = TestClient(app)

        docs_response = client.get("/docs")
        assert docs_response.status_code == 200
        assert "text/html" in docs_response.headers["content-type"]
        assert "Test" in docs_response.text
        assert "greet" in docs_response.text

        yaml_response = client.get("/mcpspec.yaml")
        assert yaml_response.status_code == 200
        assert "text/yaml" in yaml_response.headers["content-type"]
        assert "mcpspec:" in yaml_response.text
        assert "greet" in yaml_response.text

    def test_applies_exclude_filter(self) -> None:
        server = create_test_server()
        spec = McpSpec(
            server,
            info={"title": "Filter Test", "version": "1.0.0"},
            exclude=["add"],
        )

        app = spec.create_app()
        client = TestClient(app)

        response = client.get("/mcpspec.yaml")
        assert "greet" in response.text
        assert "add" not in response.text

    def test_applies_include_filter(self) -> None:
        server = create_test_server()
        spec = McpSpec(
            server,
            info={"title": "Include Test", "version": "1.0.0"},
            include=["greet"],
        )

        app = spec.create_app()
        client = TestClient(app)

        response = client.get("/mcpspec.yaml")
        assert "greet" in response.text
        assert "add" not in response.text

    def test_applies_groups(self) -> None:
        server = create_test_server()
        spec = McpSpec(
            server,
            info={"title": "Groups Test", "version": "1.0.0"},
            groups={"Greetings": ["greet"], "Math": ["add"]},
        )

        app = spec.create_app()
        client = TestClient(app)

        response = client.get("/mcpspec.yaml")
        assert "group: Greetings" in response.text
        assert "group: Math" in response.text

    def test_respects_base_path(self) -> None:
        server = create_test_server()
        spec = McpSpec(
            server,
            info={"title": "BasePath Test", "version": "1.0.0"},
            base_path="/api/v1",
        )

        app = spec.create_app()
        client = TestClient(app)

        docs = client.get("/api/v1/docs")
        assert docs.status_code == 200

        yaml_resp = client.get("/api/v1/mcpspec.yaml")
        assert yaml_resp.status_code == 200

    def test_caches_spec_after_first_request(self) -> None:
        server = create_test_server()
        spec = McpSpec(server, info={"title": "Cache Test", "version": "1.0.0"})

        app = spec.create_app()
        client = TestClient(app)

        first = client.get("/mcpspec.yaml")
        second = client.get("/mcpspec.yaml")
        assert first.status_code == 200
        assert second.status_code == 200
        assert first.text == second.text

    def test_works_with_empty_server(self) -> None:
        server = FastMCP("empty")
        spec = McpSpec(server, info={"title": "Empty", "version": "0.1.0"})

        app = spec.create_app()
        client = TestClient(app)

        docs = client.get("/docs")
        assert docs.status_code == 200
        assert "Empty" in docs.text

        yaml_resp = client.get("/mcpspec.yaml")
        assert yaml_resp.status_code == 200
        assert "mcpspec:" in yaml_resp.text

    def test_includes_transport_metadata(self) -> None:
        server = create_test_server()
        spec = McpSpec(
            server,
            info={"title": "Transport Test", "version": "1.0.0"},
            transport=[
                {
                    "type": "streamable-http",
                    "url": "/mcp",
                    "description": "Primary endpoint",
                    "auth": {"type": "bearer", "description": "Use API token"},
                }
            ],
        )

        app = spec.create_app()
        client = TestClient(app)

        response = client.get("/mcpspec.yaml")
        assert "streamable-http" in response.text
        assert "Primary endpoint" in response.text

    def test_returns_404_for_unknown_routes(self) -> None:
        server = create_test_server()
        spec = McpSpec(server, info={"title": "404 Test", "version": "1.0.0"})

        app = spec.create_app()
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/nonexistent")
        assert response.status_code == 404

    async def test_returns_503_and_logs_on_introspection_failure(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """When introspection fails, log the error and serve 503."""
        server = FastMCP("Test")
        spec_instance = McpSpec(server, info={"title": "Test", "version": "1.0"})

        # Poison the server reference so introspection fails
        spec_instance._server = None  # type: ignore[assignment]

        app = spec_instance.create_app()

        with caplog.at_level(logging.WARNING, logger="mcpspec"):
            client = TestClient(app)
            response = client.get("/docs")

        assert response.status_code == 503
        assert "mcpspec introspection failed" in caplog.text
