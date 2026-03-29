import http from "node:http";
import { createHandler } from "mcpspec";
import { server } from "./server.js";
import { API_TOKEN, tokenVerifier, extractBearerToken } from "./auth.js";

// ---------------------------------------------------------------------------
// mcpspec handler — composable with auth middleware
// ---------------------------------------------------------------------------

const handler = createHandler(server, {
  info: {
    title: "Task Manager",
    description:
      "A simple task management MCP server for demonstration.\n" +
      "Supports creating, reading, updating, and deleting tasks\n" +
      "with status tracking and priority levels.",
    version: "1.0.0",
    repository: "https://github.com/user/mcpspec",
    license: "MIT",
    authors: [{ name: "Namish Saxena", url: "https://mcpspec.dev" }],
  },
  transport: [
    {
      type: "streamable-http",
      url: "/mcp",
      description: "Primary HTTP endpoint for browser and remote clients",
      auth: {
        type: "bearer",
        description: "Set API_TOKEN env var or use the default demo token",
      },
    },
    {
      type: "stdio",
      command: "npx mcpspec-example-task-manager",
      description: "Local stdio transport for CLI and desktop clients",
    },
  ],
  groups: {
    Tasks: [
      "create_task",
      "get_task",
      "list_tasks",
      "update_task",
      "delete_task",
    ],
    Analytics: ["get_task_summary"],
  },
  examples: {
    create_task: [
      {
        title: "Create a simple task",
        input: { title: "Buy groceries", description: "Milk, eggs, bread" },
        description: "Creates a new task with default medium priority",
      },
      {
        title: "Create a high-priority task",
        input: {
          title: "Fix production bug",
          description: "Users seeing 500 errors on /api/checkout",
          priority: "high",
        },
        description: "Creates an urgent task with high priority",
      },
    ],
    list_tasks: [
      {
        title: "List in-progress tasks",
        input: { status: "in_progress", limit: 10 },
        description: "Returns up to 10 tasks that are currently in progress",
      },
      {
        title: "List high-priority todos",
        input: { status: "todo", priority: "high" },
        description: "Find all high-priority tasks that haven't been started",
      },
    ],
    get_task: [
      {
        title: "Fetch task by ID",
        input: { id: "1" },
        description: "Retrieves the full task object for task #1",
      },
    ],
  },
});

// ---------------------------------------------------------------------------
// HTTP server with auth middleware
// ---------------------------------------------------------------------------

const app = http.createServer(async (req, res) => {
  const pathname = new URL(req.url ?? "/", `http://${req.headers.host}`).pathname;
  if (pathname === "/mcp") {
    const token = extractBearerToken(req);
    if (!token) {
      res.writeHead(401, {
        "www-authenticate": 'Bearer realm="mcp"',
        "content-type": "application/json",
      });
      res.end(JSON.stringify({ error: "Bearer token required" }));
      return;
    }
    try {
      await tokenVerifier.verifyAccessToken(token);
    } catch {
      res.writeHead(401, {
        "www-authenticate": 'Bearer error="invalid_token"',
        "content-type": "application/json",
      });
      res.end(JSON.stringify({ error: "Invalid access token" }));
      return;
    }
  }

  await handler(req, res);
});

// ---------------------------------------------------------------------------
// Start server
// ---------------------------------------------------------------------------

const PORT = process.env.PORT ? parseInt(process.env.PORT, 10) : 3000;

app.listen(PORT, () => {
  console.log(`Task Manager MCP server running at http://localhost:${PORT}`);
  console.log(`  Docs:  http://localhost:${PORT}/docs          (public)`);
  console.log(`  Spec:  http://localhost:${PORT}/mcpspec.yaml   (public)`);
  console.log(`  MCP:   http://localhost:${PORT}/mcp            (bearer auth)`);
  console.log();
  if (API_TOKEN === "mcpspec-demo-token") {
    console.log(`  Auth:  Authorization: Bearer ${API_TOKEN}`);
  } else {
    console.log(`  Auth:  Authorization: Bearer <redacted>`);
  }
});
