"""Tests for mcpspec_dev.serve — Starlette route handlers."""

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.testclient import TestClient

from mcpspec_dev.serve import _build_docs_html, create_docs_route, create_yaml_route
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
        app = Starlette(
            routes=[
                Route("/docs", create_docs_route(lambda: spec), methods=["GET"]),
            ]
        )
        client = TestClient(app)

        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_html_contains_spec_title(self) -> None:
        spec = make_spec()
        app = Starlette(
            routes=[
                Route("/docs", create_docs_route(lambda: spec), methods=["GET"]),
            ]
        )
        client = TestClient(app)

        response = client.get("/docs")
        assert "Test Server" in response.text

    def test_html_contains_tool_names(self) -> None:
        spec = make_spec()
        app = Starlette(
            routes=[
                Route("/docs", create_docs_route(lambda: spec), methods=["GET"]),
            ]
        )
        client = TestClient(app)

        response = client.get("/docs")
        assert "test_tool" in response.text

    def test_returns_503_when_spec_not_ready(self) -> None:
        app = Starlette(
            routes=[
                Route("/docs", create_docs_route(lambda: None), methods=["GET"]),
            ]
        )
        client = TestClient(app)

        response = client.get("/docs")
        assert response.status_code == 503


class TestYamlRoute:
    """Test /mcpspec.yaml route handler."""

    def test_serves_yaml_with_correct_content_type(self) -> None:
        spec = make_spec()
        app = Starlette(
            routes=[
                Route("/mcpspec.yaml", create_yaml_route(lambda: spec), methods=["GET"]),
            ]
        )
        client = TestClient(app)

        response = client.get("/mcpspec.yaml")
        assert response.status_code == 200
        assert "text/yaml" in response.headers["content-type"]

    def test_yaml_contains_spec_version(self) -> None:
        spec = make_spec()
        app = Starlette(
            routes=[
                Route("/mcpspec.yaml", create_yaml_route(lambda: spec), methods=["GET"]),
            ]
        )
        client = TestClient(app)

        response = client.get("/mcpspec.yaml")
        assert "mcpspec:" in response.text
        assert "test_tool" in response.text

    def test_returns_503_when_spec_not_ready(self) -> None:
        app = Starlette(
            routes=[
                Route("/mcpspec.yaml", create_yaml_route(lambda: None), methods=["GET"]),
            ]
        )
        client = TestClient(app)

        response = client.get("/mcpspec.yaml")
        assert response.status_code == 503

    def test_yaml_contains_tool_data(self) -> None:
        spec = make_spec()
        app = Starlette(
            routes=[
                Route("/mcpspec.yaml", create_yaml_route(lambda: spec), methods=["GET"]),
            ]
        )
        client = TestClient(app)

        response = client.get("/mcpspec.yaml")
        assert "A test tool" in response.text


class TestBuildDocsHtml:
    """Test HTML template rendering edge cases."""

    def test_title_sentinel_in_tool_name_does_not_corrupt_html(self) -> None:
        """If a tool name contains __TITLE__, it must not be replaced."""
        spec = McpSpecDocument(
            mcpspec="0.1.0",
            info=McpSpecInfo(name="test", version="1.0.0", title="My Server"),
            tools=[
                McpSpecTool(name="__TITLE__", description="A tricky tool name"),
            ],
        )
        html = _build_docs_html(spec)

        # The JSON payload should contain the literal tool name "__TITLE__"
        # not the server title "My Server"
        assert "__TITLE__" in html or "\\u005f\\u005f" in html
        # The actual title should appear in the <title> tag area
        assert "My Server" in html

    def test_spec_data_sentinel_in_title_does_not_corrupt_html(self) -> None:
        """If the title contains __SPEC_DATA__, it must be escaped, not interpreted."""
        spec = McpSpecDocument(
            mcpspec="0.1.0",
            info=McpSpecInfo(name="test", version="1.0.0", title="__SPEC_DATA__"),
        )
        html = _build_docs_html(spec)

        # The page should still render (not crash or produce broken HTML)
        assert "0.1.0" in html  # spec version should be present in the JSON
