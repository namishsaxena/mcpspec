"""Tests for mcpspec_dev.serve — Starlette route handlers."""

from starlette.testclient import TestClient
from starlette.applications import Starlette
from starlette.routing import Route

from mcpspec_dev.serve import create_docs_route, create_yaml_route
from mcpspec_dev.types import McpSpecDocument, McpSpecInfo, McpSpecTool


def make_spec() -> McpSpecDocument:
    return McpSpecDocument(
        mcpspec="0.1.0",
        info=McpSpecInfo(name="test", version="1.0.0", title="Test Server"),
        tools=[McpSpecTool(name="test_tool", description="A test tool")],
        resources=[],
        prompts=[],
    )


class TestDocsRoute:
    """Test /docs route handler."""

    def test_serves_html_with_correct_content_type(self) -> None:
        spec = make_spec()
        app = Starlette(routes=[
            Route("/docs", create_docs_route(lambda: spec), methods=["GET"]),
        ])
        client = TestClient(app)

        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_html_contains_spec_title(self) -> None:
        spec = make_spec()
        app = Starlette(routes=[
            Route("/docs", create_docs_route(lambda: spec), methods=["GET"]),
        ])
        client = TestClient(app)

        response = client.get("/docs")
        assert "Test Server" in response.text

    def test_html_contains_tool_names(self) -> None:
        spec = make_spec()
        app = Starlette(routes=[
            Route("/docs", create_docs_route(lambda: spec), methods=["GET"]),
        ])
        client = TestClient(app)

        response = client.get("/docs")
        assert "test_tool" in response.text

    def test_returns_503_when_spec_not_ready(self) -> None:
        app = Starlette(routes=[
            Route("/docs", create_docs_route(lambda: None), methods=["GET"]),
        ])
        client = TestClient(app)

        response = client.get("/docs")
        assert response.status_code == 503


class TestYamlRoute:
    """Test /mcpspec.yaml route handler."""

    def test_serves_yaml_with_correct_content_type(self) -> None:
        spec = make_spec()
        app = Starlette(routes=[
            Route("/mcpspec.yaml", create_yaml_route(lambda: spec), methods=["GET"]),
        ])
        client = TestClient(app)

        response = client.get("/mcpspec.yaml")
        assert response.status_code == 200
        assert "text/yaml" in response.headers["content-type"]

    def test_yaml_contains_spec_version(self) -> None:
        spec = make_spec()
        app = Starlette(routes=[
            Route("/mcpspec.yaml", create_yaml_route(lambda: spec), methods=["GET"]),
        ])
        client = TestClient(app)

        response = client.get("/mcpspec.yaml")
        assert "mcpspec:" in response.text
        assert "test_tool" in response.text

    def test_returns_503_when_spec_not_ready(self) -> None:
        app = Starlette(routes=[
            Route("/mcpspec.yaml", create_yaml_route(lambda: None), methods=["GET"]),
        ])
        client = TestClient(app)

        response = client.get("/mcpspec.yaml")
        assert response.status_code == 503

    def test_yaml_contains_tool_data(self) -> None:
        spec = make_spec()
        app = Starlette(routes=[
            Route("/mcpspec.yaml", create_yaml_route(lambda: spec), methods=["GET"]),
        ])
        client = TestClient(app)

        response = client.get("/mcpspec.yaml")
        assert "A test tool" in response.text
