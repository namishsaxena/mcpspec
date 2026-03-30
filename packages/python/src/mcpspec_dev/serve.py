"""Starlette route handlers for /docs and /mcpspec.yaml endpoints."""

from __future__ import annotations

import html
import json
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import TYPE_CHECKING

from starlette.responses import PlainTextResponse, Response

from mcpspec_dev.generate import serialize_spec

if TYPE_CHECKING:
    from starlette.requests import Request

    from mcpspec_dev.types import McpSpecDocument

_DOCS_TEMPLATE_PATH = Path(__file__).parent / "ui" / "docs.html"

_FALLBACK_TEMPLATE = (
    "<!DOCTYPE html><html><head><title>__TITLE__</title></head>"
    "<body><pre>__SPEC_DATA__</pre></body></html>"
)


def _load_docs_template() -> str:
    try:
        return _DOCS_TEMPLATE_PATH.read_text(encoding="utf-8")
    except OSError:
        return _FALLBACK_TEMPLATE


_docs_template = _load_docs_template()


def _build_docs_html(spec: McpSpecDocument) -> str:
    """Render the docs HTML page with spec data injected."""
    title = spec.info.title or spec.info.name or "MCP Server"
    json_payload = json.dumps(
        spec.model_dump(by_alias=True, exclude_none=True),
    ).replace("</", "<\\/")
    return _docs_template.replace("__SPEC_DATA__", json_payload).replace(
        "__TITLE__", html.escape(title)
    )


GetSpec = Callable[[], "McpSpecDocument | None"]

SERVICE_UNAVAILABLE_MSG = "Spec not yet available. Server is still initializing."


def create_docs_route(
    get_spec: GetSpec,
) -> Callable[..., Awaitable[Response]]:
    """Factory that returns a Starlette endpoint serving the HTML docs page."""

    async def docs_endpoint(request: Request) -> Response:
        spec = get_spec()
        if spec is None:
            return PlainTextResponse(SERVICE_UNAVAILABLE_MSG, status_code=503)
        return Response(
            content=_build_docs_html(spec),
            media_type="text/html; charset=utf-8",
        )

    return docs_endpoint


def create_yaml_route(
    get_spec: GetSpec,
) -> Callable[..., Awaitable[Response]]:
    """Factory that returns a Starlette endpoint serving the YAML spec."""

    async def yaml_endpoint(request: Request) -> Response:
        spec = get_spec()
        if spec is None:
            return PlainTextResponse(SERVICE_UNAVAILABLE_MSG, status_code=503)
        return Response(
            content=serialize_spec(spec),
            media_type="text/yaml; charset=utf-8",
        )

    return yaml_endpoint
