# Security Guide

mcpspec is a documentation tool. It helps MCP server authors publish what their server offers. This guide explains the security model and how to control what's exposed.

## What mcpspec does

mcpspec connects to your MCP server as an in-memory client and calls:

- `tools/list` — retrieves tool names, descriptions, and schemas
- `resources/list` — retrieves resource URIs, names, and descriptions
- `prompts/list` — retrieves prompt names, descriptions, and arguments

That's it. Three read-only list operations.

## What mcpspec never does

- **Never calls `tools/call`** — it never executes your tools
- **Never calls `resources/read`** — it never reads resource content
- **Never calls `prompts/get`** — it never reads prompt templates
- **Never accesses your database, filesystem, or external APIs**
- **Never sends data to external services** — everything stays local

## How introspection works

mcpspec uses `InMemoryTransport` from the MCP SDK. This creates a direct in-memory connection between mcpspec (as a client) and your server — no HTTP, no network, no authentication layer involved.

```
External client -> HTTP -> Auth -> MCP protocol -> tools/list
                           ^ auth here

mcpspec (internal) -> InMemoryTransport -> MCP protocol -> tools/list
                      ^ no HTTP, no auth, direct
```

The introspection happens once (on first request to /docs or /mcpspec.yaml) and the result is cached.

## Controlling visibility

### Exclude patterns

Hide tools, resources, and prompts matching glob patterns:

**TypeScript:**
```typescript
mcpspec(server, {
  info: { title: "My Server", version: "1.0.0" },
  exclude: ["internal_*", "admin_*", "debug_tool"],
});
```

**Python:**
```python
McpSpec(server, info={"title": "My Server", "version": "1.0.0"},
        exclude=["internal_*", "admin_*", "debug_tool"])
```

### Include patterns (allowlist mode)

Only expose items matching specific patterns. When `include` is set, `exclude` is ignored — allowlist wins.

**TypeScript:**
```typescript
mcpspec(server, {
  info: { title: "My Server", version: "1.0.0" },
  include: ["public_*"],
});
```

**Python:**
```python
McpSpec(server, info={"title": "My Server", "version": "1.0.0"},
        include=["public_*"])
```

### Description overrides

Replace auto-generated descriptions with custom text:

**TypeScript:**
```typescript
mcpspec(server, {
  info: { title: "My Server", version: "1.0.0" },
  overrides: {
    tools: {
      "sensitive_operation": {
        description: "Performs data processing",
      },
    },
  },
});
```

**Python:**
```python
McpSpec(server, info={"title": "My Server", "version": "1.0.0"},
        overrides={"tools": {"sensitive_operation": {"description": "Performs data processing"}}})
```

## Recommendations

1. **Use `exclude` for internal tools** — prefix internal tools with `internal_` or `_` and exclude them by pattern.
2. **Use `include` for maximum control** — if you want to be explicit about what's public, use allowlist mode.
3. **Override descriptions** when auto-generated descriptions leak implementation details.
4. **Review your spec** — run your server, visit `/mcpspec.yaml`, and verify only intended information is exposed.

## Auth and mcpspec

mcpspec is auth-agnostic. It does not enforce, configure, or interfere with your server's authentication.

### TypeScript

Use `createHandler()` to compose mcpspec with your own middleware:

```typescript
import http from "node:http";
import { createHandler } from "mcpspec";

const handler = createHandler(server, options);

http.createServer(async (req, res) => {
  // Protect /mcp — docs and spec stay public
  if (new URL(req.url ?? "/", "http://localhost").pathname === "/mcp") {
    // Your auth logic here
  }
  await handler(req, res);
}).listen(3000);
```

### Python

Wrap the ASGI app with auth middleware that protects `/mcp` only:

```python
from starlette.responses import JSONResponse

_inner_app = mcp.streamable_http_app()  # FastMCP with McpSpec routes injected

async def app(scope, receive, send):
    if scope["type"] == "http" and scope["path"] == "/mcp":
        headers = dict(scope.get("headers", []))
        auth = headers.get(b"authorization", b"").decode()
        if not auth.startswith("Bearer "):
            resp = JSONResponse({"error": "Unauthorized"}, status_code=401,
                                headers={"WWW-Authenticate": "Bearer"})
            await resp(scope, receive, send)
            return
    await _inner_app(scope, receive, send)
```

### Documenting auth

This keeps `/docs` and `/mcpspec.yaml` publicly accessible (like Swagger UI) while protecting the actual MCP protocol endpoint. Introspection happens in-memory — it bypasses HTTP entirely, so your auth middleware has no effect on spec generation.

Document your auth in the `transport` option so the spec and docs UI show what auth is required:

**TypeScript:**
```typescript
createHandler(server, {
  info: { ... },
  transport: [{
    type: "streamable-http",
    url: "/mcp",
    auth: { type: "bearer", description: "API key required" },
  }],
});
```

**Python:**
```python
McpSpec(server, info={...},
        transport=[{"type": "streamable-http", "url": "/mcp",
                    "auth": {"type": "bearer", "description": "API key required"}}])
```

## Threat model

mcpspec adds three HTTP endpoints to your server:

| Endpoint | Returns | Risk |
|----------|---------|------|
| `/docs` | HTML page with tool/resource/prompt metadata | Same data as `/mcpspec.yaml`, rendered as HTML |
| `/mcpspec.yaml` | YAML spec with metadata | Exposes tool names, descriptions, and schemas |
| `/mcp` | MCP protocol endpoint | Full server access — protect with auth |

`/docs` and `/mcpspec.yaml` are designed to be public — they document what your server offers. `/mcp` is the actual protocol endpoint and should be protected when deployed.

If your tool names and descriptions are sensitive, use `exclude`/`include`/`overrides` to control visibility. If you don't want any public documentation, don't use mcpspec.

The spec is a **publication** — treat it like a README for your server.
