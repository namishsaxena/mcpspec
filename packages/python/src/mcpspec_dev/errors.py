"""Typed error classes for mcpspec-dev."""

from __future__ import annotations


class McpSpecError(Exception):
    """Base error for all mcpspec-dev operations."""


class IntrospectionError(McpSpecError):
    """Raised when MCP server introspection fails."""


class SpecGenerationError(McpSpecError):
    """Raised when spec generation fails (e.g., missing required options)."""
