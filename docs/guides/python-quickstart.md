# Python Quickstart

Get your Python MCP server documented in under 5 minutes.

## Prerequisites

- Python >= 3.10
- An existing MCP server using the `mcp` SDK

## Step 1: Install mcpspec-dev

```bash
pip install mcpspec-dev
# or
uv add mcpspec-dev
```

mcpspec-dev has minimal dependencies (`pyyaml`, `pydantic`) and expects `mcp` as a peer dependency (you already have this). It uses Starlette for route serving — which `mcp` already depends on.

## Step 2: Create your MCP server

If you don't have one yet, here's a minimal example using FastMCP:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
def greet(name: str) -> str:
    """Say hello to someone"""
    return f"Hello, {name}!"
```

## Step 3: Wrap with McpSpec

```python
from mcpspec_dev import McpSpec

spec = McpSpec(mcp, info={
    "title": "My MCP Server",
    "version": "1.0.0",
    "description": "A friendly greeting server",
})
```

For FastMCP, McpSpec automatically injects `/docs` and `/mcpspec.yaml` routes via `custom_route()`.

## Step 4: Start the server

```python
mcp.run(transport="streamable-http")
```

## Step 5: Visit /docs

Open http://localhost:8000/docs in your browser. You should see a dark-themed docs page showing your `greet` tool with its parameter schema.

## Step 6: Fetch the spec

```bash
curl http://localhost:8000/mcpspec.yaml
```

You'll get a YAML file describing your server's capabilities in a standardized format.

## Alternative: Server API with create_app()

If you use the low-level `Server` API instead of FastMCP, McpSpec can't inject routes automatically. Use `create_app()` to get a standalone Starlette ASGI app:

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

## Advanced: Auth middleware

If your MCP server uses authentication, wrap the ASGI app to protect `/mcp` while keeping docs public:

```python
from starlette.responses import JSONResponse

_inner_app = mcp.streamable_http_app()

async def app(scope, receive, send):
    if scope["type"] == "http" and scope["path"] == "/mcp":
        headers = dict(scope.get("headers", []))
        auth_header = headers.get(b"authorization", b"").decode()
        if not auth_header.startswith("Bearer "):
            response = JSONResponse(
                {"error": "Bearer token required"},
                status_code=401,
                headers={"WWW-Authenticate": "Bearer"},
            )
            await response(scope, receive, send)
            return
    await _inner_app(scope, receive, send)
```

This keeps `/docs` and `/mcpspec.yaml` publicly accessible (like Swagger UI) while protecting the actual MCP protocol endpoint.

## What's Next?

- **Add groups** to organize tools: see [Configuration Guide](./configuration.md)
- **Add examples** to tools: see [Configuration Guide](./configuration.md)
- **Add transport/auth metadata**: see [Configuration Guide](./configuration.md)
- **Control visibility** with exclude/include: see [Security Guide](./security.md)
- **Understand the spec format**: see [Spec Format Reference](./spec-format.md)

## Full Example

See the [FastMCP Task Manager example](../../examples/python/fastmcp/) and [native Server Task Manager example](../../examples/python/native/) for complete servers with groups, examples, bearer auth, multiple transport types, resources, and prompts.
