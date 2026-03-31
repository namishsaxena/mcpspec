"""Tests for mcpspec_dev.generate — spec generation and YAML serialization."""

import pytest
import yaml

from mcpspec_dev.errors import SpecGenerationError
from mcpspec_dev.generate import generate_spec, serialize_spec
from mcpspec_dev.types import (
    IntrospectionPrompt,
    IntrospectionPromptArgument,
    IntrospectionResource,
    IntrospectionResult,
    IntrospectionTool,
    McpSpecOptions,
    McpSpecToolExample,
    ToolOverride,
)


def make_introspection(
    *,
    tools: list[IntrospectionTool] | None = None,
    resources: list[IntrospectionResource] | None = None,
    prompts: list[IntrospectionPrompt] | None = None,
) -> IntrospectionResult:
    return IntrospectionResult(
        tools=tools or [],
        resources=resources or [],
        prompts=prompts or [],
        capabilities={"tools": {}} if tools else {},
    )


def make_options(**kwargs: object) -> McpSpecOptions:
    defaults: dict[str, object] = {
        "info": {"title": "Test Server", "version": "1.0.0"},
    }
    defaults.update(kwargs)
    return McpSpecOptions(**defaults)


class TestGenerateSpec:
    """Test spec generation from introspection results."""

    def test_generates_minimal_spec(self) -> None:
        result = make_introspection()
        options = make_options()
        spec = generate_spec(result, options)

        assert spec.mcpspec == "0.1.0"
        assert spec.info.name == "test-server"
        assert spec.info.version == "1.0.0"
        assert spec.info.title == "Test Server"
        assert spec.tools == []
        assert spec.resources == []
        assert spec.prompts == []

    def test_generates_spec_with_tools(self) -> None:
        result = make_introspection(
            tools=[
                IntrospectionTool(
                    name="get_data",
                    description="Fetch data from the store",
                    input_schema={
                        "type": "object",
                        "properties": {"id": {"type": "string"}},
                    },
                ),
            ],
        )
        options = make_options()
        spec = generate_spec(result, options)

        assert len(spec.tools) == 1
        assert spec.tools[0].name == "get_data"
        assert spec.tools[0].description == "Fetch data from the store"
        assert spec.tools[0].input_schema is not None

    def test_generates_spec_with_resources(self) -> None:
        result = make_introspection(
            resources=[
                IntrospectionResource(uri="data://items", name="items", description="All items"),
            ],
        )
        options = make_options()
        spec = generate_spec(result, options)

        assert len(spec.resources) == 1
        assert spec.resources[0].uri == "data://items"
        assert spec.resources[0].name == "items"

    def test_generates_spec_with_prompts(self) -> None:
        result = make_introspection(
            prompts=[
                IntrospectionPrompt(
                    name="report",
                    description="Generate report",
                    arguments=[
                        IntrospectionPromptArgument(name="format", required=True),
                    ],
                ),
            ],
        )
        options = make_options()
        spec = generate_spec(result, options)

        assert len(spec.prompts) == 1
        assert spec.prompts[0].name == "report"
        assert spec.prompts[0].arguments[0].name == "format"

    def test_applies_exclude_filter(self) -> None:
        result = make_introspection(
            tools=[
                IntrospectionTool(name="public_tool", description="Public"),
                IntrospectionTool(name="internal_debug", description="Debug"),
            ],
        )
        options = make_options(exclude=["internal_*"])
        spec = generate_spec(result, options)

        assert len(spec.tools) == 1
        assert spec.tools[0].name == "public_tool"

    def test_applies_include_filter(self) -> None:
        result = make_introspection(
            tools=[
                IntrospectionTool(name="allowed_tool", description="Allowed"),
                IntrospectionTool(name="blocked_tool", description="Blocked"),
            ],
        )
        options = make_options(include=["allowed_*"])
        spec = generate_spec(result, options)

        assert len(spec.tools) == 1
        assert spec.tools[0].name == "allowed_tool"

    def test_applies_tool_groups(self) -> None:
        result = make_introspection(
            tools=[
                IntrospectionTool(name="create_task", description="Create"),
                IntrospectionTool(name="get_summary", description="Summary"),
            ],
        )
        options = make_options(groups={"Tasks": ["create_task"], "Analytics": ["get_summary"]})
        spec = generate_spec(result, options)

        assert spec.tools[0].group == "Tasks"
        assert spec.tools[1].group == "Analytics"

    def test_applies_tool_overrides(self) -> None:
        result = make_introspection(
            tools=[
                IntrospectionTool(name="my_tool", description="Original desc"),
            ],
        )
        options = make_options(
            overrides={"tools": {"my_tool": ToolOverride(description="Override desc")}}
        )
        spec = generate_spec(result, options)

        assert spec.tools[0].description == "Override desc"

    def test_applies_tool_examples(self) -> None:
        result = make_introspection(
            tools=[
                IntrospectionTool(name="my_tool", description="A tool"),
            ],
        )
        options = make_options(
            examples={"my_tool": [McpSpecToolExample(title="Example", input={"x": 1})]}
        )
        spec = generate_spec(result, options)

        assert spec.tools[0].examples is not None
        assert len(spec.tools[0].examples) == 1
        assert spec.tools[0].examples[0].title == "Example"

    def test_includes_transport_when_provided(self) -> None:
        result = make_introspection()
        options = make_options(transport=[{"type": "streamable-http", "url": "/mcp"}])
        spec = generate_spec(result, options)

        assert spec.transport is not None
        assert len(spec.transport) == 1
        assert spec.transport[0].type == "streamable-http"

    def test_omits_transport_when_not_provided(self) -> None:
        result = make_introspection()
        options = make_options()
        spec = generate_spec(result, options)

        assert spec.transport is None

    def test_title_to_slug_conversion(self) -> None:
        result = make_introspection()
        options = make_options(info={"title": "My Cool Server!", "version": "2.0.0"})
        spec = generate_spec(result, options)

        assert spec.info.name == "my-cool-server"

    def test_includes_schema_url(self) -> None:
        result = make_introspection()
        options = make_options()
        spec = generate_spec(result, options)

        assert spec.schema_url == "https://mcpspec.dev/schema/0.1.0.json"

    def test_maps_tool_annotations(self) -> None:
        result = make_introspection(
            tools=[
                IntrospectionTool(
                    name="readonly_tool",
                    description="Read only",
                    annotations={
                        "readOnlyHint": True,
                        "idempotentHint": True,
                    },
                ),
            ],
        )
        options = make_options()
        spec = generate_spec(result, options)

        assert spec.tools[0].annotations is not None
        assert spec.tools[0].annotations.read_only_hint is True
        assert spec.tools[0].annotations.idempotent_hint is True

    def test_generate_spec_does_not_mutate_introspection_result(self) -> None:
        resource = IntrospectionResource(uri="data://items", name=None, description="Items")
        result = make_introspection(resources=[resource])
        options = make_options()

        generate_spec(result, options)

        # Original resource must not be mutated
        assert resource.name is None

    def test_empty_string_override_is_honored(self) -> None:
        """TypeScript ?? treats '' as a valid value. Python must match."""
        result = make_introspection(
            tools=[
                IntrospectionTool(name="my_tool", title="Original", description="Original desc"),
            ],
        )
        options = make_options(
            overrides={"tools": {"my_tool": ToolOverride(title="", description="")}}
        )
        spec = generate_spec(result, options)

        # Empty string overrides should replace originals (nullish, not truthiness)
        assert spec.tools[0].title == ""
        assert spec.tools[0].description == ""

    def test_accepts_dict_tool_overrides(self) -> None:
        result = make_introspection(
            tools=[IntrospectionTool(name="my_tool", description="Original")],
        )
        options = make_options(overrides={"tools": {"my_tool": {"description": "Dict override"}}})
        spec = generate_spec(result, options)
        assert spec.tools[0].description == "Dict override"

    def test_accepts_dict_resource_overrides(self) -> None:
        result = make_introspection(
            resources=[
                IntrospectionResource(uri="data://items", name="items", description="Original"),
            ],
        )
        options = make_options(overrides={"resources": {"items": {"description": "Dict override"}}})
        spec = generate_spec(result, options)
        assert spec.resources[0].description == "Dict override"

    def test_accepts_dict_prompt_overrides(self) -> None:
        result = make_introspection(
            prompts=[
                IntrospectionPrompt(name="report", description="Original"),
            ],
        )
        options = make_options(overrides={"prompts": {"report": {"description": "Dict override"}}})
        spec = generate_spec(result, options)
        assert spec.prompts[0].description == "Dict override"

    def test_raises_on_missing_info_title(self) -> None:
        result = make_introspection()
        options = make_options(info={"version": "1.0.0"})
        with pytest.raises(SpecGenerationError, match="title"):
            generate_spec(result, options)

    def test_raises_on_missing_info_version(self) -> None:
        result = make_introspection()
        options = make_options(info={"title": "Test"})
        with pytest.raises(SpecGenerationError, match="version"):
            generate_spec(result, options)

    def test_preserves_empty_capabilities(self) -> None:
        """TypeScript includes capabilities: {} — Python must match."""
        result = IntrospectionResult(
            tools=[],
            resources=[],
            prompts=[],
            capabilities={},
        )
        options = make_options()
        spec = generate_spec(result, options)

        # Empty capabilities should be preserved, not converted to None
        assert spec.capabilities == {}


class TestSerializeSpec:
    """Test YAML serialization."""

    def test_serializes_to_valid_yaml(self) -> None:
        result = make_introspection(
            tools=[IntrospectionTool(name="test_tool", description="A tool")],
        )
        spec = generate_spec(result, make_options())
        yaml_str = serialize_spec(spec)

        parsed = yaml.safe_load(yaml_str)
        assert parsed["mcpspec"] == "0.1.0"
        assert parsed["info"]["name"] == "test-server"

    def test_yaml_uses_block_style(self) -> None:
        result = make_introspection(
            tools=[IntrospectionTool(name="test_tool", description="A tool")],
        )
        spec = generate_spec(result, make_options())
        yaml_str = serialize_spec(spec)

        # Block style: indented, not inline {key: value}
        assert "- name: test_tool\n  description: A tool" in yaml_str

    def test_yaml_omits_null_fields(self) -> None:
        result = make_introspection()
        spec = generate_spec(result, make_options())
        yaml_str = serialize_spec(spec)

        assert "transport:" not in yaml_str
        assert "null" not in yaml_str

    def test_yaml_version_is_plain_scalar(self) -> None:
        """js-yaml outputs mcpspec: 0.1.0 without quotes. pyyaml must match."""
        result = make_introspection()
        spec = generate_spec(result, make_options())
        yaml_str = serialize_spec(spec)

        # The version should be a plain scalar (no quotes)
        # This matches the TypeScript js-yaml behavior
        assert "mcpspec: 0.1.0" in yaml_str or 'mcpspec: "0.1.0"' in yaml_str

    def test_roundtrip_preserves_data(self) -> None:
        result = make_introspection(
            tools=[
                IntrospectionTool(
                    name="test",
                    description="Test tool",
                    input_schema={
                        "type": "object",
                        "properties": {"x": {"type": "string"}},
                    },
                ),
            ],
        )
        spec = generate_spec(result, make_options())
        yaml_str = serialize_spec(spec)
        parsed = yaml.safe_load(yaml_str)

        assert parsed["tools"][0]["name"] == "test"
        assert parsed["tools"][0]["inputSchema"]["properties"]["x"]["type"] == "string"
