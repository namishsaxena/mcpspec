"""mcpspec-dev: OpenAPI-like specs for MCP servers."""

from mcpspec_dev.filter import filter_items, match_glob
from mcpspec_dev.generate import generate_spec, serialize_spec
from mcpspec_dev.introspect import introspect
from mcpspec_dev.types import (
    IntrospectionPrompt,
    IntrospectionPromptArgument,
    IntrospectionResource,
    IntrospectionResult,
    IntrospectionTool,
    McpSpec,
    McpSpecAuth,
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
    "filter_items",
    "generate_spec",
    "introspect",
    "match_glob",
    "serialize_spec",
    "IntrospectionPrompt",
    "IntrospectionPromptArgument",
    "IntrospectionResource",
    "IntrospectionResult",
    "IntrospectionTool",
    "McpSpec",
    "McpSpecAuth",
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
    "ToolOverride",
]
