# Configuration Guide

## TypeScript

All configuration is passed as the second argument to `mcpspec()` or `createHandler()`.

```typescript
// Simple — returns an http.Server directly
const app = mcpspec(server, options);

// Composable — returns a request handler you can wrap with middleware
const handler = createHandler(server, options);
const app = http.createServer((req, res) => {
  // Add auth, CORS, logging, etc. here
  handler(req, res);
});
```

Use `createHandler()` when you need middleware (auth, logging, CORS). Use `mcpspec()` for simple servers with no middleware needs.

## Python

All configuration is passed as keyword arguments to the `McpSpec` constructor.

```python
from mcpspec import McpSpec

# FastMCP — routes injected automatically via custom_route()
spec = McpSpec(mcp, info={"title": "My Server", "version": "1.0.0"})

# Server API — use create_app() for a standalone Starlette ASGI app
spec = McpSpec(server, info={"title": "My Server", "version": "1.0.0"})
app = spec.create_app()
```

Use `create_app()` with the low-level Server API. FastMCP servers get routes injected automatically.

## Required: `info`

The only required field. Provides metadata about your server.

```typescript
{
  info: {
    title: "My Server",            // Required. Display name in docs header.
    version: "1.0.0",              // Required. Server version shown in docs.
    description: "What it does",   // Optional. Shown below the title.
    repository: "https://...",     // Optional. Link in docs header.
    license: "MIT",                // Optional. SPDX identifier.
    serverUrl: "https://...",      // Optional. Canonical production URL.
    authors: [                     // Optional. Shown in docs.
      { name: "Jane Doe", url: "https://github.com/janedoe" },
    ],
  },
}
```

## Optional: `transport`

Document how clients connect to your server. This is purely informational — mcpspec does not configure or enforce transport behavior, it just documents it in the spec and docs UI.

A server can expose multiple transports. Each transport has its own auth requirements (or none). This is why auth is nested inside transport — a stdio transport has no auth, while an HTTP transport might require a bearer token.

```typescript
{
  transport: [
    {
      type: "streamable-http",
      url: "https://my-server.com/mcp",
      description: "Primary HTTP endpoint for remote clients",
      auth: {
        type: "bearer",
        description: "Use your API key from the dashboard",
      },
    },
    {
      type: "stdio",
      command: "npx @my-org/my-server",
      description: "Local transport for CLI and desktop clients",
    },
  ],
}
```

### Transport types

| Type | Fields |
|------|--------|
| `streamable-http` | `url`, `description`, `auth` |
| `stdio` | `command`, `description` |

### Auth types

Auth is per-transport. A `stdio` transport typically has no auth (local process), while `streamable-http` usually does.

| Type | Fields |
|------|--------|
| `oauth2` | `tokenUrl`, `scopes`, `description` |
| `bearer` | `description` |
| `api-key` | `description` |
| `none` | `description` (explicit no-auth) |

## Optional: `basePath`

Prefix all mcpspec routes. Useful when mcpspec shares a port with other services.

```typescript
{
  basePath: "/api/v1",
  // Routes become: /api/v1/docs, /api/v1/mcpspec.yaml
}
```

Default: `""` (routes at root: `/docs`, `/mcpspec.yaml`).

## Optional: `exclude`

Hide tools, resources, and prompts matching glob patterns.

```typescript
{
  exclude: ["internal_*", "admin_debug_*", "secret_tool"],
}
```

Glob patterns support `*` (any characters) and `?` (single character).

## Optional: `include`

Allowlist mode — only items matching these patterns appear in the spec. When `include` is set, `exclude` is ignored.

```typescript
{
  include: ["public_*"],
  // Only tools/resources/prompts starting with "public_" will be documented
}
```

## Optional: `groups`

Organize tools into collapsible groups in the docs UI. Each key is the group name, and the value is an array of tool names.

```typescript
{
  groups: {
    "Data": ["get_users", "list_items", "search"],
    "Admin": ["reset_cache", "clear_logs"],
    "Analytics": ["get_metrics"],
  },
}
```

Tools not in any group appear under "Ungrouped".

## Optional: `examples`

Add usage examples to tools. Each example has a title, input object, and optional description.

```typescript
{
  examples: {
    "get_users": [
      {
        title: "Fetch first 10 users",
        input: { limit: 10 },
        description: "Returns a paginated list of users",
      },
      {
        title: "Search by email",
        input: { email: "jane@example.com" },
      },
    ],
  },
}
```

Examples appear in the tool detail card with a copy-to-clipboard button.

## Optional: `overrides`

Override auto-generated metadata for specific tools, resources, or prompts. Useful for redacting sensitive descriptions or adding context that isn't in the tool definition.

```typescript
{
  overrides: {
    tools: {
      "sensitive_tool": {
        description: "Performs secure data processing",  // replaces auto-generated
        group: "Security",                                // override group
        title: "Data Processor",                          // override display title
      },
    },
    resources: {
      "config://internal": {
        description: "Server configuration (read-only)",
      },
    },
    prompts: {
      "internal_prompt": {
        description: "System prompt for internal use",
      },
    },
  },
}
```

### Override fields

| Target | Available overrides |
|--------|-------------------|
| Tools | `description`, `group`, `title` |
| Resources | `description` |
| Prompts | `description` |

## Full Example — TypeScript (simple — no auth)

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { mcpspec } from "mcpspec";

const server = new McpServer({ name: "my-server", version: "1.0.0" });
// ... register tools ...

const app = mcpspec(server, {
  info: {
    title: "My MCP Server",
    version: "1.0.0",
    description: "Does useful things with data",
    repository: "https://github.com/me/my-server",
    license: "MIT",
  },
  transport: [
    {
      type: "streamable-http",
      url: "/mcp",
      description: "HTTP endpoint",
    },
    {
      type: "stdio",
      command: "npx @my-org/my-server",
      description: "Local CLI transport",
    },
  ],
  exclude: ["internal_*"],
  groups: {
    Data: ["get_users", "list_items"],
    Admin: ["reset_cache"],
  },
  examples: {
    get_users: [
      { title: "Fetch 10 users", input: { limit: 10 } },
    ],
  },
});

app.listen(3000);
```

## Full Example — TypeScript (with auth)

Use `createHandler()` to wrap the handler with auth middleware. `/docs` and `/mcpspec.yaml` stay public, `/mcp` requires auth — same pattern as OpenAPI/Swagger UI.

```typescript
import http from "node:http";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { createHandler } from "mcpspec";

const server = new McpServer({ name: "my-server", version: "1.0.0" });
// ... register tools ...

const handler = createHandler(server, {
  info: {
    title: "My MCP Server",
    version: "1.0.0",
    description: "Does useful things with data",
  },
  transport: [
    {
      type: "streamable-http",
      url: "/mcp",
      description: "HTTP endpoint with bearer auth",
      auth: {
        type: "bearer",
        description: "Use your API key from the dashboard",
      },
    },
    {
      type: "stdio",
      command: "npx @my-org/my-server",
      description: "Local transport — no auth needed",
    },
  ],
  groups: {
    Data: ["get_users", "list_items"],
  },
});

const app = http.createServer(async (req, res) => {
  const pathname = new URL(req.url ?? "/", "http://localhost").pathname;
  if (pathname === "/mcp") {
    const auth = req.headers.authorization;
    if (!auth?.startsWith("Bearer ")) {
      res.writeHead(401, { "www-authenticate": "Bearer" });
      res.end(JSON.stringify({ error: "Bearer token required" }));
      return;
    }
    // Validate token here...
  }
  await handler(req, res);
});

app.listen(3000);
```

## Full Example — Python (FastMCP)

```python
from mcp.server.fastmcp import FastMCP
from mcpspec import McpSpec

mcp = FastMCP("my-server")
# ... register tools with @mcp.tool() ...

spec = McpSpec(
    mcp,
    info={
        "title": "My MCP Server",
        "version": "1.0.0",
        "description": "Does useful things with data",
        "repository": "https://github.com/me/my-server",
        "license": "MIT",
    },
    transport=[
        {
            "type": "streamable-http",
            "url": "/mcp",
            "description": "HTTP endpoint",
        },
        {
            "type": "stdio",
            "command": "python -m my_server",
            "description": "Local CLI transport",
        },
    ],
    exclude=["internal_*"],
    groups={
        "Data": ["get_users", "list_items"],
        "Admin": ["reset_cache"],
    },
    examples={
        "get_users": [
            {"title": "Fetch 10 users", "input": {"limit": 10}},
        ],
    },
)

mcp.run(transport="streamable-http")
```

## Full Example — Python (Server API with auth)

Use `create_app()` with the low-level Server, then compose with auth middleware:

```python
from mcp.server.lowlevel import Server
from mcpspec import McpSpec
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
import uvicorn

server = Server("my-server")
# ... register tools ...

spec = McpSpec(
    server,
    info={
        "title": "My MCP Server",
        "version": "1.0.0",
    },
    transport=[
        {
            "type": "streamable-http",
            "url": "/mcp",
            "auth": {"type": "bearer", "description": "API key required"},
        },
    ],
    groups={"Data": ["get_users", "list_items"]},
)

_app = Starlette(routes=[
    Route("/docs", spec._handle_docs, methods=["GET"]),
    Route("/mcpspec.yaml", spec._handle_yaml, methods=["GET"]),
    Route("/mcp", mcp_transport),  # your MCP transport handler
])

async def app(scope, receive, send):
    if scope["type"] == "http" and scope["path"] == "/mcp":
        headers = dict(scope.get("headers", []))
        auth = headers.get(b"authorization", b"").decode()
        if not auth.startswith("Bearer "):
            resp = JSONResponse({"error": "Unauthorized"}, status_code=401)
            await resp(scope, receive, send)
            return
    await _app(scope, receive, send)

uvicorn.run(app, port=3000)
```
