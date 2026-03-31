"""McpSpec class — primary public API for mcpspec-dev.

Provides route injection for FastMCP servers and standalone ASGI app
via create_app(). Lazy introspection with caching and error recovery.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse, Response
from starlette.routing import Route

from mcpspec_dev.generate import generate_spec, serialize_spec
from mcpspec_dev.introspect import introspect
from mcpspec_dev.serve import SERVICE_UNAVAILABLE_MSG, _build_docs_html
from mcpspec_dev.types import McpSpecDocument, McpSpecOptions

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP
    from mcp.server.lowlevel.server import Server
    from starlette.requests import Request

logger = logging.getLogger("mcpspec")


class McpSpec:
    """Generate and serve MCP specs via Starlette routes.

    Detects FastMCP for automatic route injection via custom_route().
    create_app() returns a standalone Starlette ASGI app.
    """

    def __init__(
        self,
        server: FastMCP | Server[object],
        *,
        info: dict[str, Any],
        transport: list[dict[str, Any]] | None = None,
        base_path: str = "",
        exclude: list[str] | None = None,
        include: list[str] | None = None,
        overrides: dict[str, Any] | None = None,
        groups: dict[str, list[str]] | None = None,
        examples: dict[str, list[Any]] | None = None,
    ) -> None:
        self._server = server
        self._options = McpSpecOptions(
            info=info,
            transport=transport,
            base_path=base_path,
            exclude=exclude,
            include=include,
            overrides=overrides,
            groups=groups,
            examples=examples,
        )
        self._cached_spec: McpSpecDocument | None = None
        self._introspection_lock = asyncio.Lock()

        if _is_fastmcp(server):
            self._inject_routes(server)  # type: ignore[arg-type]

    async def _ensure_spec(self) -> McpSpecDocument | None:
        """Lazily introspect and cache the spec. Returns None on failure."""
        if self._cached_spec is not None:
            return self._cached_spec
        async with self._introspection_lock:
            if self._cached_spec is not None:
                return self._cached_spec
            try:
                result = await introspect(self._server)
                self._cached_spec = generate_spec(result, self._options)
                return self._cached_spec
            except Exception:
                logger.warning("mcpspec introspection failed", exc_info=True)
                return None

    async def _handle_docs(self, request: Request) -> Response:
        """Serve the HTML documentation page."""
        spec = await self._ensure_spec()
        if spec is None:
            return PlainTextResponse(SERVICE_UNAVAILABLE_MSG, status_code=503)
        return Response(
            content=_build_docs_html(spec),
            media_type="text/html; charset=utf-8",
        )

    async def _handle_yaml(self, request: Request) -> Response:
        """Serve the YAML spec file."""
        spec = await self._ensure_spec()
        if spec is None:
            return PlainTextResponse(SERVICE_UNAVAILABLE_MSG, status_code=503)
        return Response(
            content=serialize_spec(spec),
            media_type="text/yaml; charset=utf-8",
        )

    def create_app(self) -> Starlette:
        """Return a standalone Starlette ASGI app with /docs and /mcpspec.yaml."""
        base = (self._options.base_path or "").rstrip("/")
        return Starlette(
            routes=[
                Route(f"{base}/docs", self._handle_docs, methods=["GET"]),
                Route(f"{base}/mcpspec.yaml", self._handle_yaml, methods=["GET"]),
            ]
        )

    def _inject_routes(self, server: FastMCP) -> None:
        """Register /docs and /mcpspec.yaml on a FastMCP server."""
        base = (self._options.base_path or "").rstrip("/")
        instance = self

        @server.custom_route(f"{base}/docs", methods=["GET"])  # type: ignore[untyped-decorator]
        async def docs_handler(request: Request) -> Response:
            return await instance._handle_docs(request)

        @server.custom_route(f"{base}/mcpspec.yaml", methods=["GET"])  # type: ignore[untyped-decorator]
        async def yaml_handler(request: Request) -> Response:
            return await instance._handle_yaml(request)


def _is_fastmcp(server: object) -> bool:
    """Check if server is a FastMCP instance without importing it."""
    return type(server).__name__ == "FastMCP"
