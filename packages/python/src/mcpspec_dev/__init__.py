"""mcpspec-dev: OpenAPI-like specs for MCP servers."""

from mcpspec_dev.errors import IntrospectionError, McpSpecError, SpecGenerationError
from mcpspec_dev.filter import filter_items, match_glob
from mcpspec_dev.generate import generate_spec, serialize_spec
from mcpspec_dev.introspect import introspect
from mcpspec_dev.mcpspec import McpSpec
from mcpspec_dev.serve import create_docs_route, create_yaml_route
from mcpspec_dev.types import (
    IntrospectionPrompt,
    IntrospectionPromptArgument,
    IntrospectionResource,
    IntrospectionResult,
    IntrospectionTool,
    McpSpecAuth,
    McpSpecAuthor,
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
    PromptOverride,
    ResourceOverride,
    ToolOverride,
)

__all__ = [
    "IntrospectionError",
    "IntrospectionPrompt",
    "IntrospectionPromptArgument",
    "IntrospectionResource",
    "IntrospectionResult",
    "IntrospectionTool",
    "McpSpec",
    "McpSpecAuth",
    "McpSpecAuthor",
    "McpSpecDocument",
    "McpSpecError",
    "McpSpecInfo",
    "McpSpecOptions",
    "McpSpecPrompt",
    "McpSpecPromptArgument",
    "McpSpecResource",
    "McpSpecTool",
    "McpSpecToolAnnotations",
    "McpSpecToolExample",
    "McpSpecTransport",
    "PromptOverride",
    "ResourceOverride",
    "SpecGenerationError",
    "ToolOverride",
    "create_docs_route",
    "create_yaml_route",
    "filter_items",
    "generate_spec",
    "introspect",
    "match_glob",
    "serialize_spec",
]
