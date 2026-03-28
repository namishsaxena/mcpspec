# Configuration Guide

All configuration is passed as the second argument to `mcpspec()`.

```typescript
const app = mcpspec(server, options);
```

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

Document how clients connect to your server. This is purely informational — mcpspec does not configure transport behavior.

```typescript
{
  transport: [
    {
      type: "streamable-http",
      url: "https://my-server.com/mcp",
      auth: {
        type: "oauth2",
        tokenUrl: "https://my-server.com/oauth/token",
        scopes: ["read", "write"],
      },
    },
    {
      type: "stdio",
      command: "npx @my-org/my-server",
    },
  ],
}
```

### Transport types

| Type | Fields |
|------|--------|
| `streamable-http` | `url` (required), `auth` (optional) |
| `stdio` | `command` (required) |

### Auth types

| Type | Fields |
|------|--------|
| `oauth2` | `tokenUrl`, `scopes` |
| `bearer` | (no additional fields) |
| `api-key` | (no additional fields) |
| `none` | (explicit no-auth) |

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

## Full Example

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
    authors: [{ name: "Me" }],
  },
  transport: [
    {
      type: "streamable-http",
      url: "https://my-server.com/mcp",
      auth: { type: "bearer" },
    },
  ],
  basePath: "/spec",
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
  overrides: {
    tools: {
      reset_cache: { description: "Clears the application cache" },
    },
  },
});

app.listen(3000, () => {
  console.log("http://localhost:3000/spec/docs");
});
```
