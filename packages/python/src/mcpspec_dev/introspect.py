"""MCP server introspection via in-memory transport.

Connects to a FastMCP or Server instance, extracts tools, resources, prompts,
and capabilities using only MCP list endpoints. Never calls get/read/call.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mcp.shared.memory import create_connected_server_and_client_session

from mcpspec_dev.types import (
    IntrospectionPrompt,
    IntrospectionPromptArgument,
    IntrospectionResource,
    IntrospectionResult,
    IntrospectionTool,
)

if TYPE_CHECKING:
    from mcp.client.session import ClientSession
    from mcp.server.fastmcp import FastMCP
    from mcp.server.lowlevel.server import Server
    from mcp.types import ServerCapabilities


async def introspect(
    server: FastMCP | Server[object],
) -> IntrospectionResult:
    """Introspect an MCP server and return its tools, resources, and prompts."""
    async with create_connected_server_and_client_session(
        server,
    ) as session:
        await session.initialize()

        caps = session.get_server_capabilities()
        capabilities = _extract_capabilities(caps)

        tools = await _list_all_tools(session) if caps and caps.tools else []
        resources = (
            await _list_all_resources(session) if caps and caps.resources else []
        )
        prompts = (
            await _list_all_prompts(session) if caps and caps.prompts else []
        )

        return IntrospectionResult(
            tools=tools,
            resources=resources,
            prompts=prompts,
            capabilities=capabilities,
        )


def _extract_capabilities(
    caps: ServerCapabilities | None,
) -> dict[str, Any]:
    """Convert ServerCapabilities to a plain dict, keeping only object values."""
    if caps is None:
        return {}
    result: dict[str, Any] = {}
    for key, value in caps.model_dump().items():
        if isinstance(value, dict):
            result[key] = value
        elif value is not None:
            result[key] = {}
    return result


async def _list_all_tools(
    session: ClientSession,
) -> list[IntrospectionTool]:
    """List all tools with pagination support."""
    tools: list[IntrospectionTool] = []
    cursor: str | None = None

    while True:
        response = await session.list_tools(cursor)
        for tool in response.tools:
            tools.append(
                IntrospectionTool(
                    name=tool.name,
                    title=getattr(tool, "title", None),
                    description=tool.description,
                    annotations=_annotations_to_dict(tool.annotations),
                    input_schema=dict(tool.inputSchema) if tool.inputSchema else None,
                    output_schema=getattr(tool, "outputSchema", None),
                ),
            )
        cursor = response.nextCursor
        if not cursor:
            break

    return tools


async def _list_all_resources(
    session: ClientSession,
) -> list[IntrospectionResource]:
    """List all resources with pagination support."""
    resources: list[IntrospectionResource] = []
    cursor: str | None = None

    while True:
        response = await session.list_resources(cursor)
        for resource in response.resources:
            resources.append(
                IntrospectionResource(
                    uri=str(resource.uri),
                    name=resource.name,
                    description=resource.description,
                    mime_type=resource.mimeType,
                ),
            )
        cursor = response.nextCursor
        if not cursor:
            break

    return resources


async def _list_all_prompts(
    session: ClientSession,
) -> list[IntrospectionPrompt]:
    """List all prompts with pagination support."""
    prompts: list[IntrospectionPrompt] = []
    cursor: str | None = None

    while True:
        response = await session.list_prompts(cursor)
        for prompt in response.prompts:
            arguments = None
            if prompt.arguments:
                arguments = [
                    IntrospectionPromptArgument(
                        name=arg.name,
                        description=arg.description,
                        required=arg.required,
                    )
                    for arg in prompt.arguments
                ]
            prompts.append(
                IntrospectionPrompt(
                    name=prompt.name,
                    description=prompt.description,
                    arguments=arguments,
                ),
            )
        cursor = response.nextCursor
        if not cursor:
            break

    return prompts


def _annotations_to_dict(
    annotations: object,
) -> dict[str, Any] | None:
    """Convert tool annotations to a plain dict, or None if absent."""
    if annotations is None:
        return None
    if hasattr(annotations, "model_dump"):
        data: dict[str, Any] = annotations.model_dump(exclude_none=True)
        return data if data else None
    return None
