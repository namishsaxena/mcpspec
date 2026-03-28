---
description: MCP protocol rules specific to mcpspec
---

# MCP Protocol Rules

## Allowed Methods

mcpspec is an introspection-only tool. It ONLY calls these MCP methods:

- `initialize` — establish connection and learn server capabilities
- `tools/list` — enumerate available tools (metadata only)
- `resources/list` — enumerate available resources (metadata only)
- `resources/listTemplates` — enumerate resource templates (metadata only)
- `prompts/list` — enumerate available prompts (metadata only)

## Forbidden Methods

mcpspec NEVER calls:

- `tools/call` — would execute server-side code (crosses introspection boundary)
- `prompts/get` — would retrieve prompt content, not just metadata
- `resources/read` — would access resource content, not just metadata
- `resources/subscribe` — would open persistent connections beyond introspection

If you find yourself needing to call a forbidden method, stop and reconsider the approach. The spec is a publication of metadata, not a proxy for server interaction.

## Transport

- Introspection uses `InMemoryTransport` from the MCP SDK.
- mcpspec never touches the HTTP layer or authentication — it connects directly to the server's request handler in-process.

## Publication Philosophy

- The spec is a **publication**, not a dump. Server authors control what is exposed.
- The `McpSpecOptions` type lets authors include/exclude tools, resources, and prompts.
- Default behavior: include everything the server exposes. Filtering is opt-in.

## Pagination

- Always handle `nextCursor` when calling list endpoints.
- A list method may return partial results with a cursor for the next page.
- Loop until `nextCursor` is `undefined` or `null`.

## Resource Cleanup

- Always close transport connections in `finally` blocks.
- If introspection fails mid-way, the transport must still be cleaned up.
- Never leave dangling connections.
