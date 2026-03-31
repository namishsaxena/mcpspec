"""Spec generation and YAML serialization for mcpspec documents."""

from __future__ import annotations

import re
from typing import Any

import yaml

from mcpspec_dev.filter import filter_items
from mcpspec_dev.types import (
    IntrospectionPrompt,
    IntrospectionResource,
    IntrospectionResult,
    IntrospectionTool,
    McpSpecAuthor,
    McpSpecDocument,
    McpSpecInfo,
    McpSpecOptions,
    McpSpecPrompt,
    McpSpecPromptArgument,
    McpSpecResource,
    McpSpecTool,
    McpSpecToolAnnotations,
    McpSpecTransport,
    PromptOverride,
    ResourceOverride,
    ToolOverride,
)

MCPSPEC_VERSION = "0.1.0"
SCHEMA_URL = f"https://mcpspec.dev/schema/{MCPSPEC_VERSION}.json"


def generate_spec(
    introspection: IntrospectionResult,
    options: McpSpecOptions,
) -> McpSpecDocument:
    """Transform introspection results into an McpSpecDocument."""
    include = options.include
    exclude = options.exclude

    filtered_tools = filter_items(introspection.tools, include=include, exclude=exclude)
    # Resources have name guaranteed after _ensure_resource_names (name ?? uri)
    filtered_resources = filter_items(
        _ensure_resource_names(introspection.resources),  # type: ignore[type-var]
        include=include,
        exclude=exclude,
    )
    filtered_prompts = filter_items(introspection.prompts, include=include, exclude=exclude)

    tools = [_map_tool(t, options) for t in filtered_tools]
    resources = [_map_resource(r, options) for r in filtered_resources]
    prompts = [_map_prompt(p, options) for p in filtered_prompts]

    transport = _build_transport(options)

    return McpSpecDocument(
        mcpspec=MCPSPEC_VERSION,
        schema_url=SCHEMA_URL,
        info=McpSpecInfo(
            name=_title_to_slug(options.info["title"]),
            version=options.info["version"],
            title=options.info.get("title"),
            description=options.info.get("description"),
            server_url=options.info.get("serverUrl"),
            repository=options.info.get("repository"),
            license=options.info.get("license"),
            authors=_parse_authors(options.info.get("authors")),
        ),
        capabilities=introspection.capabilities or None,
        tools=tools,
        resources=resources,
        prompts=prompts,
        transport=transport,
    )


def serialize_spec(spec: McpSpecDocument) -> str:
    """Serialize an McpSpecDocument to YAML matching TypeScript output."""
    data = spec.model_dump(by_alias=True, exclude_none=True)
    result: str = yaml.dump(
        data,
        indent=2,
        width=120,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    )
    return result


def _ensure_resource_names(
    resources: list[IntrospectionResource],
) -> list[IntrospectionResource]:
    """Return new resources with name defaulting to uri. Does not mutate input."""
    return [
        IntrospectionResource(
            uri=r.uri,
            name=r.name if r.name is not None else r.uri,
            description=r.description,
            mime_type=r.mime_type,
        )
        for r in resources
    ]


def _map_tool(
    tool: IntrospectionTool,
    options: McpSpecOptions,
) -> McpSpecTool:
    """Map an introspection tool to a spec tool with overrides."""
    override = _get_tool_override(tool.name, options)
    group = _find_group(tool.name, options.groups)
    examples = options.examples.get(tool.name) if options.examples else None

    return McpSpecTool(
        name=tool.name,
        title=override.title if override is not None and override.title is not None else tool.title,
        description=(
            override.description
            if override is not None and override.description is not None
            else tool.description
        ),
        group=override.group if override is not None and override.group is not None else group,
        annotations=_map_annotations(tool.annotations),
        input_schema=tool.input_schema,
        output_schema=tool.output_schema,
        examples=examples,
    )


def _map_resource(
    resource: IntrospectionResource,
    options: McpSpecOptions,
) -> McpSpecResource:
    """Map an introspection resource to a spec resource with overrides."""
    override = _get_resource_override(resource.name or resource.uri, options)

    return McpSpecResource(
        uri=resource.uri,
        name=resource.name,
        description=(
            override.description
            if override is not None and override.description is not None
            else resource.description
        ),
        mime_type=resource.mime_type,
    )


def _map_prompt(
    prompt: IntrospectionPrompt,
    options: McpSpecOptions,
) -> McpSpecPrompt:
    """Map an introspection prompt to a spec prompt with overrides."""
    override = _get_prompt_override(prompt.name, options)

    arguments = None
    if prompt.arguments:
        arguments = [
            McpSpecPromptArgument(
                name=arg.name,
                description=arg.description,
                required=arg.required,
            )
            for arg in prompt.arguments
        ]

    return McpSpecPrompt(
        name=prompt.name,
        description=(
            override.description
            if override is not None and override.description is not None
            else prompt.description
        ),
        arguments=arguments,
    )


def _map_annotations(
    raw: dict[str, Any] | None,
) -> McpSpecToolAnnotations | None:
    """Extract known annotation booleans from raw annotations dict."""
    if not raw:
        return None

    result = McpSpecToolAnnotations()
    if isinstance(raw.get("readOnlyHint"), bool):
        result.read_only_hint = raw["readOnlyHint"]
    if isinstance(raw.get("destructiveHint"), bool):
        result.destructive_hint = raw["destructiveHint"]
    if isinstance(raw.get("idempotentHint"), bool):
        result.idempotent_hint = raw["idempotentHint"]
    if isinstance(raw.get("openWorldHint"), bool):
        result.open_world_hint = raw["openWorldHint"]

    has_values = any(
        v is not None
        for v in [
            result.read_only_hint,
            result.destructive_hint,
            result.idempotent_hint,
            result.open_world_hint,
        ]
    )
    return result if has_values else None


def _get_tool_override(name: str, options: McpSpecOptions) -> ToolOverride | None:
    """Look up a tool override from options. Accepts ToolOverride or raw dict."""
    overrides = options.overrides or {}
    tool_overrides: dict[str, Any] = overrides.get("tools", {})
    override = tool_overrides.get(name)
    if override is None:
        return None
    if isinstance(override, ToolOverride):
        return override
    if isinstance(override, dict):
        return ToolOverride(**override)
    return None


def _get_resource_override(key: str, options: McpSpecOptions) -> ResourceOverride | None:
    """Look up a resource override from options. Accepts ResourceOverride or raw dict."""
    overrides = options.overrides or {}
    resource_overrides: dict[str, Any] = overrides.get("resources", {})
    override = resource_overrides.get(key)
    if override is None:
        return None
    if isinstance(override, ResourceOverride):
        return override
    if isinstance(override, dict):
        return ResourceOverride(**override)
    return None


def _get_prompt_override(name: str, options: McpSpecOptions) -> PromptOverride | None:
    """Look up a prompt override from options. Accepts PromptOverride or raw dict."""
    overrides = options.overrides or {}
    prompt_overrides: dict[str, Any] = overrides.get("prompts", {})
    override = prompt_overrides.get(name)
    if override is None:
        return None
    if isinstance(override, PromptOverride):
        return override
    if isinstance(override, dict):
        return PromptOverride(**override)
    return None


def _find_group(
    tool_name: str,
    groups: dict[str, list[str]] | None,
) -> str | None:
    """Look up which group a tool belongs to."""
    if not groups:
        return None
    for group_name, tool_names in groups.items():
        if tool_name in tool_names:
            return group_name
    return None


def _build_transport(
    options: McpSpecOptions,
) -> list[McpSpecTransport] | None:
    """Build transport list from options, or None if empty."""
    if not options.transport:
        return None
    return [McpSpecTransport(**t) for t in options.transport]


def _title_to_slug(title: str) -> str:
    """Convert a title to a URL-friendly slug."""
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def _parse_authors(
    raw: list[dict[str, Any]] | list[McpSpecAuthor] | None,
) -> list[McpSpecAuthor] | None:
    """Parse authors from raw dicts or McpSpecAuthor objects."""
    if not raw:
        return None
    return [a if isinstance(a, McpSpecAuthor) else McpSpecAuthor(**a) for a in raw]
