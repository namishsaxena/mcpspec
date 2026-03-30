"""Glob-based include/exclude filtering for MCP items."""

from __future__ import annotations

import re
from typing import Protocol, TypeVar


class Named(Protocol):
    """Protocol for items that have a name attribute."""

    @property
    def name(self) -> str: ...


T = TypeVar("T", bound=Named)

_REGEX_SPECIAL = frozenset(r"\.+^${}()|[]")


def filter_items(
    items: list[T],
    *,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
) -> list[T]:
    """Filter items by name using glob patterns.

    Include mode (allowlist) takes precedence over exclude mode when both are set.
    """
    if include is not None:
        return [item for item in items if any(match_glob(item.name, p) for p in include)]

    if exclude is not None and len(exclude) > 0:
        return [item for item in items if not any(match_glob(item.name, p) for p in exclude)]

    return list(items)


def match_glob(name: str, pattern: str) -> bool:
    """Match a name against a glob pattern (* and ? wildcards)."""
    regex_str = _glob_to_regex(pattern)
    return bool(re.fullmatch(regex_str, name))


def _glob_to_regex(pattern: str) -> str:
    """Convert a glob pattern to a regex string."""
    result: list[str] = []
    for char in pattern:
        if char == "*":
            result.append(".*")
        elif char == "?":
            result.append(".")
        elif char in _REGEX_SPECIAL:
            result.append(f"\\{char}")
        else:
            result.append(char)
    return "".join(result)
