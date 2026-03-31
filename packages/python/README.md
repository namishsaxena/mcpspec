# mcpspec-dev

OpenAPI-like specs for Python MCP servers. One line of code. Zero config.

mcpspec wraps your MCP server, introspects its tools, resources, and prompts via the MCP protocol, and serves:
- `/docs` — interactive HTML documentation (dark/light/high-contrast themes, no CDN)
- `/mcpspec.yaml` — a machine-readable spec in a standardized format

## Install

```bash
pip install mcpspec-dev
# or
uv add mcpspec-dev
```

## Quick Start (FastMCP)

```python
from mcp.server.fastmcp import FastMCP
from mcpspec_dev import McpSpec

mcp = FastMCP("my-server")

@mcp.tool()
def greet(name: str) -> str:
    """Say hello to someone"""
    return f"Hello, {name}!"

spec = McpSpec(mcp, info={"title": "My Server", "version": "1.0.0"})
mcp.run(transport="streamable-http")
```

Visit `http://localhost:8000/docs` and `http://localhost:8000/mcpspec.yaml`.

## Quick Start (Server API)

```python
from mcp.server.lowlevel import Server
from mcpspec_dev import McpSpec
import uvicorn

server = Server("my-server")
# Register tools via @server.call_tool(), etc.

spec = McpSpec(server, info={"title": "My Server", "version": "1.0.0"})
app = spec.create_app()
uvicorn.run(app, port=3000)
```

## What It Does

1. **Introspects** your MCP server at first request (lazy, cached)
2. **Generates** a `mcpspec.yaml` spec with tools, resources, prompts, and metadata
3. **Serves** human-readable docs and the raw spec as HTTP endpoints
4. **Injects routes** on FastMCP via `custom_route()` — or use `create_app()` for standalone ASGI

## Options

```python
spec = McpSpec(
    server,
    info={
        "title": "My Server",           # Required: display name
        "version": "1.0.0",             # Required: server version
        "description": "Does things",   # Optional
        "repository": "https://...",    # Optional: source repo URL
        "license": "MIT",               # Optional: SPDX identifier
        "serverUrl": "https://...",     # Optional: production URL
        "authors": [{"name": "You"}],  # Optional
    },
    transport=[{                        # Optional: document connection methods
        "type": "streamable-http",
        "url": "https://my-server.com/mcp",
        "auth": {"type": "bearer"},
    }],
    base_path="/api",                   # Optional: prefix all routes
    exclude=["internal_*"],             # Optional: hide tools by glob pattern
    include=["public_*"],              # Optional: allowlist mode (overrides exclude)
    groups={                            # Optional: group tools in the docs UI
        "Data": ["get_users", "list_items"],
        "Admin": ["reset_cache"],
    },
    examples={                          # Optional: add usage examples to tools
        "get_users": [{
            "title": "Fetch first 10 users",
            "input": {"limit": 10},
        }],
    },
)
```

## Security

**Your spec, your rules.** mcpspec is a documentation tool, not a surveillance tool.

- Only calls `tools/list`, `resources/list`, `prompts/list` — never reads content or executes tools
- Introspects via in-memory transport — bypasses HTTP/auth entirely
- Use `exclude`/`include` to control what appears in the spec
- Use `overrides` to redact or rewrite descriptions

See the [security guide](https://github.com/namishsaxena/mcpspec/blob/main/docs/guides/security.md) for details.

## Links

- **Docs & Viewer:** [mcpspec.dev](https://mcpspec.dev)
- **GitHub:** [github.com/namishsaxena/mcpspec](https://github.com/namishsaxena/mcpspec)
- **Spec Format:** [Spec Format Reference](https://github.com/namishsaxena/mcpspec/blob/main/docs/guides/spec-format.md)
- **TypeScript:** [@mcpspec-dev/typescript on npm](https://www.npmjs.com/package/@mcpspec-dev/typescript)

## License

MIT
