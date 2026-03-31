"""Tests for mcpspec_dev.types — Pydantic model validation and serialization."""

from mcpspec_dev.types import (
    IntrospectionPrompt,
    IntrospectionPromptArgument,
    IntrospectionResource,
    IntrospectionResult,
    IntrospectionTool,
    McpSpecAuth,
    McpSpecDocument,
    McpSpecInfo,
    McpSpecOptions,
    McpSpecPrompt,
    McpSpecPromptArgument,
    McpSpecResource,
    McpSpecTool,
    McpSpecToolAnnotations,
    McpSpecToolExample,
    McpSpecTransport,
    ToolOverride,
)


class TestMcpSpecModels:
    """Test McpSpecDocument models."""

    def test_minimal_spec(self) -> None:
        spec = McpSpecDocument(
            mcpspec="0.1.0",
            info=McpSpecInfo(name="test", version="1.0.0"),
        )
        assert spec.mcpspec == "0.1.0"
        assert spec.info.name == "test"
        assert spec.tools is None
        assert spec.resources is None
        assert spec.prompts is None

    def test_full_spec(self) -> None:
        spec = McpSpecDocument(
            mcpspec="0.1.0",
            schema_url="https://mcpspec.dev/schema/0.1.0.json",
            info=McpSpecInfo(
                name="my-server",
                version="1.0.0",
                title="My Server",
                description="A test server",
                server_url="http://localhost:3000",
                repository="https://github.com/user/repo",
                license="MIT",
                authors=[{"name": "Test Author", "url": "https://example.com"}],
            ),
            transport=[
                McpSpecTransport(
                    type="streamable-http",
                    url="/mcp",
                    description="Primary HTTP endpoint",
                    auth=McpSpecAuth(
                        type="bearer",
                        description="Set API_TOKEN env var",
                    ),
                ),
            ],
            tools=[
                McpSpecTool(
                    name="my_tool",
                    title="My Tool",
                    description="Does things",
                    group="Utils",
                    annotations=McpSpecToolAnnotations(read_only_hint=True),
                    input_schema={"type": "object", "properties": {"x": {"type": "string"}}},
                    examples=[
                        McpSpecToolExample(title="Example", input={"x": "hello"}),
                    ],
                ),
            ],
            resources=[
                McpSpecResource(uri="data://items", name="items", description="All items"),
            ],
            prompts=[
                McpSpecPrompt(
                    name="report",
                    description="Generate report",
                    arguments=[
                        McpSpecPromptArgument(
                            name="format",
                            description="Output format",
                            required=True,
                        ),
                    ],
                ),
            ],
        )
        assert spec.info.title == "My Server"
        assert len(spec.tools) == 1
        assert spec.tools[0].annotations.read_only_hint is True
        assert len(spec.transport) == 1
        assert spec.transport[0].auth.type == "bearer"

    def test_spec_serialization_excludes_none(self) -> None:
        spec = McpSpecDocument(
            mcpspec="0.1.0",
            info=McpSpecInfo(name="test", version="1.0.0"),
        )
        data = spec.model_dump(exclude_none=True)
        assert "tools" not in data
        assert "transport" not in data
        assert "schema_url" not in data

    def test_spec_serialization_uses_camel_case_aliases(self) -> None:
        spec = McpSpecDocument(
            mcpspec="0.1.0",
            schema_url="https://mcpspec.dev/schema/0.1.0.json",
            info=McpSpecInfo(name="test", version="1.0.0", server_url="http://localhost"),
        )
        data = spec.model_dump(by_alias=True, exclude_none=True)
        assert "$schema" in data
        assert "serverUrl" in data["info"]

    def test_info_authors_accepts_mcpspec_author_objects(self) -> None:
        from mcpspec_dev.types import McpSpecAuthor

        info = McpSpecInfo(
            name="test",
            version="1.0.0",
            authors=[McpSpecAuthor(name="Alice", url="https://alice.dev")],
        )
        assert info.authors is not None
        assert len(info.authors) == 1
        assert info.authors[0].name == "Alice"
        assert info.authors[0].url == "https://alice.dev"

    def test_info_authors_serializes_correctly(self) -> None:
        from mcpspec_dev.types import McpSpecAuthor

        info = McpSpecInfo(
            name="test",
            version="1.0.0",
            authors=[McpSpecAuthor(name="Bob")],
        )
        data = info.model_dump(exclude_none=True)
        assert data["authors"] == [{"name": "Bob"}]

    def test_tool_annotations_all_fields(self) -> None:
        ann = McpSpecToolAnnotations(
            read_only_hint=True,
            destructive_hint=False,
            idempotent_hint=True,
            open_world_hint=False,
        )
        data = ann.model_dump(by_alias=True, exclude_none=True)
        assert data["readOnlyHint"] is True
        assert data["destructiveHint"] is False


class TestIntrospectionModels:
    """Test introspection result models."""

    def test_introspection_result(self) -> None:
        result = IntrospectionResult(
            tools=[
                IntrospectionTool(
                    name="test_tool",
                    description="A tool",
                    input_schema={"type": "object"},
                ),
            ],
            resources=[
                IntrospectionResource(uri="data://test", name="test"),
            ],
            prompts=[
                IntrospectionPrompt(
                    name="test_prompt",
                    arguments=[
                        IntrospectionPromptArgument(name="arg1", required=True),
                    ],
                ),
            ],
            capabilities={"tools": {}},
        )
        assert len(result.tools) == 1
        assert result.tools[0].name == "test_tool"
        assert len(result.resources) == 1
        assert len(result.prompts) == 1
        assert result.prompts[0].arguments[0].required is True

    def test_empty_introspection_result(self) -> None:
        result = IntrospectionResult(
            tools=[],
            resources=[],
            prompts=[],
            capabilities={},
        )
        assert len(result.tools) == 0
        assert len(result.resources) == 0
        assert len(result.prompts) == 0


class TestOptionsModels:
    """Test user-provided options models."""

    def test_minimal_options(self) -> None:
        opts = McpSpecOptions(
            info={"title": "Test", "version": "1.0.0"},
        )
        assert opts.info["title"] == "Test"
        assert opts.exclude is None
        assert opts.include is None

    def test_full_options(self) -> None:
        opts = McpSpecOptions(
            info={"title": "Test", "version": "1.0.0", "description": "A test"},
            transport=[{"type": "streamable-http", "url": "/mcp"}],
            base_path="/api",
            exclude=["internal_*"],
            include=None,
            overrides={
                "tools": {"my_tool": ToolOverride(description="Override desc")},
            },
            groups={"Utils": ["my_tool"]},
            examples={"my_tool": [McpSpecToolExample(title="Ex", input={"x": 1})]},
        )
        assert opts.base_path == "/api"
        assert "internal_*" in opts.exclude
        assert opts.overrides["tools"]["my_tool"].description == "Override desc"
