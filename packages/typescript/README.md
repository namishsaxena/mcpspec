# @mcpspec-dev/typescript

OpenAPI-like specs for MCP servers. One line of code. Zero config.

mcpspec wraps your MCP server, introspects its tools, resources, and prompts via the MCP protocol, and serves:
- `/docs` — interactive HTML documentation (dark/light/high-contrast themes, no CDN)
- `/mcpspec.yaml` — a machine-readable spec in a standardized format

## Install

```bash
npm install @mcpspec-dev/typescript
```

## Quick Start

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { mcpspec } from "@mcpspec-dev/typescript";

const server = new McpServer({ name: "my-server", version: "1.0.0" });

// Register your tools, resources, prompts as usual...

const app = mcpspec(server, {
  info: { title: "My MCP Server", version: "1.0.0" },
});

app.listen(3000, () => {
  console.log("http://localhost:3000/docs");
  console.log("http://localhost:3000/mcpspec.yaml");
});
```

## What It Does

1. **Introspects** your MCP server at first request (lazy, cached)
2. **Generates** a `mcpspec.yaml` spec with tools, resources, prompts, and metadata
3. **Serves** human-readable docs and the raw spec as HTTP endpoints
4. **Proxies MCP** at `/mcp` — clients connect via Streamable HTTP

## Options

```typescript
const app = mcpspec(server, {
  info: {
    title: "My Server",           // Required: display name
    version: "1.0.0",             // Required: server version
    description: "Does things",   // Optional
    repository: "https://...",    // Optional: source repo URL
    license: "MIT",               // Optional: SPDX identifier
    serverUrl: "https://...",     // Optional: production URL
    authors: [{ name: "You" }],  // Optional
  },
  transport: [{                   // Optional: document connection methods
    type: "streamable-http",
    url: "https://my-server.com/mcp",
    auth: { type: "bearer" },
  }],
  basePath: "/api",               // Optional: prefix all routes
  exclude: ["internal_*"],        // Optional: hide tools by glob pattern
  include: ["public_*"],          // Optional: allowlist mode (overrides exclude)
  groups: {                       // Optional: group tools in the docs UI
    "Data": ["get_users", "list_items"],
    "Admin": ["reset_cache"],
  },
  examples: {                     // Optional: add usage examples to tools
    "get_users": [{
      title: "Fetch first 10 users",
      input: { limit: 10 },
      description: "Returns paginated user list",
    }],
  },
  overrides: {                    // Optional: override auto-generated metadata
    tools: {
      "sensitive_tool": { description: "Performs data processing" },
    },
  },
});
```

## Security

**Your spec, your rules.** mcpspec is a documentation tool, not a surveillance tool.

- Only calls `tools/list`, `resources/list`, `prompts/list` — never reads content or executes tools
- Introspects via in-memory transport — bypasses HTTP/auth entirely
- Use `exclude`/`include` to control what appears in the spec
- Use `overrides` to redact or rewrite descriptions

See the [security guide](https://github.com/namishsaxena/mcpspec/blob/main/docs/guides/security.md) for details.

## Spec Format

The generated `mcpspec.yaml` follows a standardized format with JSON Schema validation:

```yaml
mcpspec: 0.1.0
$schema: "https://mcpspec.dev/schema/0.1.0.json"
info:
  name: my-server
  version: "1.0.0"
  title: My MCP Server
tools:
  - name: get_users
    description: Retrieve registered users
    inputSchema: { ... }
resources: []
prompts: []
```

## Links

- **Docs & Viewer:** [mcpspec.dev](https://mcpspec.dev)
- **GitHub:** [github.com/namishsaxena/mcpspec](https://github.com/namishsaxena/mcpspec)
- **npm:** [npmjs.com/package/@mcpspec-dev/typescript](https://www.npmjs.com/package/@mcpspec-dev/typescript)

## License

MIT
