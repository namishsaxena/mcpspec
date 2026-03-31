"""Pydantic models for mcpspec document format, user options, and introspection."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# mcpspec.yaml format types — mirror the YAML structure exactly
# ---------------------------------------------------------------------------


class McpSpecAuthor(BaseModel):
    """Author information."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    url: str | None = None


class McpSpecAuth(BaseModel):
    """Authentication configuration for a transport."""

    model_config = ConfigDict(populate_by_name=True)

    type: str
    token_url: str | None = Field(default=None, alias="tokenUrl")
    scopes: list[str] | None = None
    description: str | None = None


class McpSpecTransport(BaseModel):
    """Transport configuration."""

    model_config = ConfigDict(populate_by_name=True)

    type: str
    url: str | None = None
    command: str | None = None
    description: str | None = None
    auth: McpSpecAuth | None = None


class McpSpecInfo(BaseModel):
    """Server metadata."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    version: str
    title: str | None = None
    description: str | None = None
    server_url: str | None = Field(default=None, alias="serverUrl")
    repository: str | None = None
    license: str | None = None
    authors: list[McpSpecAuthor] | None = None


class McpSpecToolAnnotations(BaseModel):
    """Tool behavior annotations."""

    model_config = ConfigDict(populate_by_name=True)

    read_only_hint: bool | None = Field(default=None, alias="readOnlyHint")
    destructive_hint: bool | None = Field(default=None, alias="destructiveHint")
    idempotent_hint: bool | None = Field(default=None, alias="idempotentHint")
    open_world_hint: bool | None = Field(default=None, alias="openWorldHint")


class McpSpecToolExample(BaseModel):
    """Tool usage example."""

    model_config = ConfigDict(populate_by_name=True)

    title: str
    input: dict[str, Any]
    description: str | None = None


class McpSpecTool(BaseModel):
    """Tool definition in the spec document."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    title: str | None = None
    description: str | None = None
    group: str | None = None
    annotations: McpSpecToolAnnotations | None = None
    input_schema: dict[str, Any] | None = Field(default=None, alias="inputSchema")
    output_schema: dict[str, Any] | None = Field(default=None, alias="outputSchema")
    examples: list[McpSpecToolExample] | None = None


class McpSpecResource(BaseModel):
    """Resource definition in the spec document."""

    model_config = ConfigDict(populate_by_name=True)

    uri: str
    name: str | None = None
    description: str | None = None
    mime_type: str | None = Field(default=None, alias="mimeType")


class McpSpecPromptArgument(BaseModel):
    """Prompt argument definition."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    description: str | None = None
    required: bool | None = None


class McpSpecPrompt(BaseModel):
    """Prompt definition in the spec document."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    description: str | None = None
    arguments: list[McpSpecPromptArgument] | None = None


class McpSpecDocument(BaseModel):
    """Root mcpspec document model."""

    model_config = ConfigDict(populate_by_name=True)

    mcpspec: str
    schema_url: str | None = Field(default=None, alias="$schema")
    info: McpSpecInfo
    transport: list[McpSpecTransport] | None = None
    capabilities: dict[str, dict[str, Any] | dict[str, Any]] | None = None
    tools: list[McpSpecTool] | None = None
    resources: list[McpSpecResource] | None = None
    prompts: list[McpSpecPrompt] | None = None


# ---------------------------------------------------------------------------
# Introspection result types — raw data from MCP protocol
# ---------------------------------------------------------------------------


class IntrospectionTool(BaseModel):
    """Tool as returned by MCP tools/list."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    title: str | None = None
    description: str | None = None
    annotations: dict[str, Any] | None = None
    input_schema: dict[str, Any] | None = Field(default=None, alias="inputSchema")
    output_schema: dict[str, Any] | None = Field(default=None, alias="outputSchema")


class IntrospectionResource(BaseModel):
    """Resource as returned by MCP resources/list."""

    model_config = ConfigDict(populate_by_name=True)

    uri: str
    name: str | None = None
    description: str | None = None
    mime_type: str | None = Field(default=None, alias="mimeType")


class IntrospectionPromptArgument(BaseModel):
    """Prompt argument as returned by MCP prompts/list."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    description: str | None = None
    required: bool | None = None


class IntrospectionPrompt(BaseModel):
    """Prompt as returned by MCP prompts/list."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    description: str | None = None
    arguments: list[IntrospectionPromptArgument] | None = None


class IntrospectionResult(BaseModel):
    """Complete result of MCP server introspection."""

    model_config = ConfigDict(populate_by_name=True)

    tools: list[IntrospectionTool]
    resources: list[IntrospectionResource]
    prompts: list[IntrospectionPrompt]
    capabilities: dict[str, Any]


# ---------------------------------------------------------------------------
# Options types — passed by the user to mcpspec()
# ---------------------------------------------------------------------------


class ToolOverride(BaseModel):
    """Override fields for a specific tool."""

    model_config = ConfigDict(populate_by_name=True)

    description: str | None = None
    group: str | None = None
    title: str | None = None


class ResourceOverride(BaseModel):
    """Override fields for a specific resource."""

    model_config = ConfigDict(populate_by_name=True)

    description: str | None = None


class PromptOverride(BaseModel):
    """Override fields for a specific prompt."""

    model_config = ConfigDict(populate_by_name=True)

    description: str | None = None


class McpSpecOptions(BaseModel):
    """User-provided options for mcpspec generation."""

    model_config = ConfigDict(populate_by_name=True)

    info: dict[str, Any]
    transport: list[dict[str, Any]] | None = None
    base_path: str | None = Field(default=None, alias="basePath")
    exclude: list[str] | None = None
    include: list[str] | None = None
    overrides: dict[str, Any] | None = None
    groups: dict[str, list[str]] | None = None
    examples: dict[str, list[McpSpecToolExample]] | None = None
