# TypeScript Quickstart

Get your MCP server documented in under 5 minutes.

## Prerequisites

- Node.js >= 18
- An existing MCP server using `@modelcontextprotocol/sdk`

## Step 1: Install mcpspec

```bash
pnpm add mcpspec
```

mcpspec has one dependency (`js-yaml`) and expects `@modelcontextprotocol/sdk` as a peer dependency (you already have this). It uses raw Node.js `http` for serving — no framework dependency.

## Step 2: Create your MCP server

If you don't have one yet, here's a minimal example:

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const server = new McpServer({
  name: "my-server",
  version: "1.0.0",
});

server.registerTool(
  "greet",
  {
    description: "Say hello to someone",
    inputSchema: { name: z.string().describe("Name to greet") },
  },
  async ({ name }) => ({
    content: [{ type: "text", text: `Hello, ${name}!` }],
  })
);
```

## Step 3: Wrap with mcpspec

```typescript
import { mcpspec } from "mcpspec";

const app = mcpspec(server, {
  info: {
    title: "My MCP Server",
    version: "1.0.0",
    description: "A friendly greeting server",
  },
});
```

## Step 4: Start the server

```typescript
app.listen(3000, () => {
  console.log("Server running at http://localhost:3000");
  console.log("  Docs: http://localhost:3000/docs");
  console.log("  Spec: http://localhost:3000/mcpspec.yaml");
});
```

## Step 5: Visit /docs

Open http://localhost:3000/docs in your browser. You should see a dark-themed docs page showing your `greet` tool with its parameter schema.

## Step 6: Fetch the spec

```bash
curl http://localhost:3000/mcpspec.yaml
```

You'll get a YAML file describing your server's capabilities in a standardized format.

## What's Next?

- **Add groups** to organize tools: see [Configuration Guide](./configuration.md)
- **Add examples** to tools: see [Configuration Guide](./configuration.md)
- **Control visibility** with exclude/include: see [Security Guide](./security.md)
- **Understand the spec format**: see [Spec Format Reference](./spec-format.md)

## Full Example

See the [Task Manager example](../../examples/typescript/src/index.ts) for a complete server with groups, examples, resources, and prompts.
