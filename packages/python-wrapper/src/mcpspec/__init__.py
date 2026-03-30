"""mcpspec — convenience wrapper for mcpspec-dev.

Install: pip install mcpspec
Import: from mcpspec import McpSpec
"""

from mcpspec_dev import (
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
    generate_spec,
    introspect,
    serialize_spec,
)

__all__ = [
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
    "generate_spec",
    "introspect",
    "serialize_spec",
]
