"""Cross-language parity tests.

Verify that Python generates the same mcpspec.yaml structure as TypeScript
for equivalent server configurations. Uses fixture data representing
known TypeScript output.
"""

import yaml

from mcpspec_dev.generate import generate_spec, serialize_spec
from mcpspec_dev.types import (
    IntrospectionPrompt,
    IntrospectionResource,
    IntrospectionResult,
    IntrospectionTool,
    McpSpecOptions,
    McpSpecToolExample,
)


def make_task_manager_introspection() -> IntrospectionResult:
    """Create introspection result matching the TypeScript Task Manager example."""
    return IntrospectionResult(
        tools=[
            IntrospectionTool(
                name="create_task",
                description="Create a new task with a title, optional description, and priority",
                input_schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Task title"},
                        "description": {
                            "type": "string",
                            "description": "Detailed task description",
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                            "description": "Task priority level (defaults to medium)",
                        },
                    },
                    "required": ["title"],
                },
                annotations={
                    "readOnlyHint": False,
                    "idempotentHint": False,
                    "openWorldHint": False,
                },
            ),
            IntrospectionTool(
                name="get_task",
                description="Retrieve a single task by its ID",
                input_schema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "Task ID"},
                    },
                    "required": ["id"],
                },
                annotations={
                    "readOnlyHint": True,
                    "idempotentHint": True,
                    "openWorldHint": False,
                },
            ),
        ],
        resources=[
            IntrospectionResource(
                uri="tasks://summary",
                name="task-summary",
                mime_type="application/json",
            ),
        ],
        prompts=[
            IntrospectionPrompt(
                name="task_report",
                description="Generate a task status report for the current sprint",
                arguments=[],
            ),
        ],
        capabilities={"tools": {}, "resources": {}, "prompts": {}},
    )


def make_task_manager_options() -> McpSpecOptions:
    """Create options matching the TypeScript Task Manager example."""
    return McpSpecOptions(
        info={
            "title": "Task Manager",
            "version": "1.0.0",
            "description": "A simple task management MCP server",
        },
        groups={
            "Tasks": ["create_task", "get_task"],
            "Analytics": [],
        },
        examples={
            "create_task": [
                McpSpecToolExample(
                    title="Create a simple task",
                    input={"title": "Buy groceries"},
                    description="Creates a new task with default medium priority",
                ),
            ],
        },
        transport=[
            {
                "type": "streamable-http",
                "url": "/mcp",
                "auth": {"type": "bearer"},
            }
        ],
    )


class TestCrossLanguageParity:
    """Verify Python output matches TypeScript structure."""

    def test_spec_has_same_top_level_keys(self) -> None:
        introspection = make_task_manager_introspection()
        options = make_task_manager_options()
        spec = generate_spec(introspection, options)

        data = spec.model_dump(by_alias=True, exclude_none=True)

        for key in [
            "mcpspec",
            "$schema",
            "info",
            "tools",
            "resources",
            "prompts",
            "transport",
            "capabilities",
        ]:
            assert key in data, f"Missing top-level key: {key}"

    def test_info_block_matches_typescript(self) -> None:
        introspection = make_task_manager_introspection()
        options = make_task_manager_options()
        spec = generate_spec(introspection, options)

        data = spec.model_dump(by_alias=True, exclude_none=True)
        info = data["info"]

        assert info["name"] == "task-manager"
        assert info["version"] == "1.0.0"
        assert info["title"] == "Task Manager"
        assert info["description"] == "A simple task management MCP server"

    def test_tool_structure_matches_typescript(self) -> None:
        introspection = make_task_manager_introspection()
        options = make_task_manager_options()
        spec = generate_spec(introspection, options)

        data = spec.model_dump(by_alias=True, exclude_none=True)
        create_task = next(t for t in data["tools"] if t["name"] == "create_task")

        assert "inputSchema" in create_task
        assert "annotations" in create_task
        assert "group" in create_task
        assert create_task["group"] == "Tasks"

        # Annotations use camelCase (matching TypeScript output)
        assert "readOnlyHint" in create_task["annotations"]
        assert create_task["annotations"]["readOnlyHint"] is False

    def test_yaml_serialization_style(self) -> None:
        """YAML output should use same formatting as TypeScript js-yaml."""
        introspection = make_task_manager_introspection()
        options = make_task_manager_options()
        spec = generate_spec(introspection, options)
        yaml_str = serialize_spec(spec)

        parsed = yaml.safe_load(yaml_str)
        assert parsed is not None

        # Block style (not inline/flow)
        assert "- name: create_task" in yaml_str

        # No null/None values in output
        assert "null" not in yaml_str

        # Has 2-space indented lines (block style)
        lines = yaml_str.strip().split("\n")
        indented = [line for line in lines if line.startswith("  ")]
        assert len(indented) > 0

    def test_roundtrip_yaml_preserves_all_data(self) -> None:
        introspection = make_task_manager_introspection()
        options = make_task_manager_options()
        spec = generate_spec(introspection, options)
        yaml_str = serialize_spec(spec)
        parsed = yaml.safe_load(yaml_str)

        # All tools present
        tool_names = [t["name"] for t in parsed["tools"]]
        assert "create_task" in tool_names
        assert "get_task" in tool_names

        # All resources present
        assert len(parsed["resources"]) == 1
        assert parsed["resources"][0]["uri"] == "tasks://summary"

        # All prompts present
        assert len(parsed["prompts"]) == 1
        assert parsed["prompts"][0]["name"] == "task_report"

        # Transport present
        assert parsed["transport"][0]["type"] == "streamable-http"
        assert parsed["transport"][0]["auth"]["type"] == "bearer"
