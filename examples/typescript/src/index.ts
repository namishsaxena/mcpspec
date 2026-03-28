import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { mcpspec } from "mcpspec";

// ---------------------------------------------------------------------------
// In-memory task store
// ---------------------------------------------------------------------------

interface Task {
  id: string;
  title: string;
  description: string;
  status: "todo" | "in_progress" | "done";
  priority: "low" | "medium" | "high";
  createdAt: string;
  updatedAt: string;
}

const tasks = new Map<string, Task>();
let nextId = 1;

function now(): string {
  return new Date().toISOString();
}

// ---------------------------------------------------------------------------
// MCP server
// ---------------------------------------------------------------------------

const server = new McpServer({
  name: "task-manager",
  version: "1.0.0",
});

// --- Tasks group ---

server.registerTool(
  "create_task",
  {
    description: "Create a new task with a title, optional description, and priority",
    annotations: { readOnlyHint: false, idempotentHint: false, openWorldHint: false },
    inputSchema: {
      title: z.string().describe("Task title"),
      description: z.string().optional().describe("Detailed task description"),
      priority: z
        .enum(["low", "medium", "high"])
        .optional()
        .describe("Task priority level (defaults to medium)"),
    },
  },
  async ({ title, description, priority }) => {
    const id = String(nextId++);
    const task: Task = {
      id,
      title,
      description: description ?? "",
      status: "todo",
      priority: priority ?? "medium",
      createdAt: now(),
      updatedAt: now(),
    };
    tasks.set(id, task);
    return {
      content: [{ type: "text", text: JSON.stringify(task, null, 2) }],
    };
  }
);

server.registerTool(
  "get_task",
  {
    description: "Retrieve a single task by its ID",
    annotations: { readOnlyHint: true, idempotentHint: true, openWorldHint: false },
    inputSchema: {
      id: z.string().describe("Task ID"),
    },
  },
  async ({ id }) => {
    const task = tasks.get(id);
    if (!task) {
      return {
        content: [{ type: "text", text: `Task ${id} not found` }],
        isError: true,
      };
    }
    return {
      content: [{ type: "text", text: JSON.stringify(task, null, 2) }],
    };
  }
);

server.registerTool(
  "list_tasks",
  {
    description: "List tasks with optional filtering by status and priority",
    annotations: { readOnlyHint: true, idempotentHint: true, openWorldHint: false },
    inputSchema: {
      status: z
        .enum(["todo", "in_progress", "done"])
        .optional()
        .describe("Filter by task status"),
      priority: z
        .enum(["low", "medium", "high"])
        .optional()
        .describe("Filter by priority level"),
      limit: z
        .number()
        .int()
        .min(1)
        .max(100)
        .optional()
        .describe("Maximum number of tasks to return (default: 25, max: 100)"),
    },
  },
  async ({ status, priority, limit }) => {
    let result = Array.from(tasks.values());
    if (status) {
      result = result.filter((t) => t.status === status);
    }
    if (priority) {
      result = result.filter((t) => t.priority === priority);
    }
    result = result.slice(0, limit ?? 25);
    return {
      content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
    };
  }
);

server.registerTool(
  "update_task",
  {
    description: "Update fields on an existing task",
    annotations: { readOnlyHint: false, idempotentHint: true, openWorldHint: false },
    inputSchema: {
      id: z.string().describe("Task ID"),
      title: z.string().optional().describe("New title"),
      description: z.string().optional().describe("New description"),
      status: z
        .enum(["todo", "in_progress", "done"])
        .optional()
        .describe("New status"),
      priority: z
        .enum(["low", "medium", "high"])
        .optional()
        .describe("New priority"),
    },
  },
  async ({ id, title, description, status, priority }) => {
    const task = tasks.get(id);
    if (!task) {
      return {
        content: [{ type: "text", text: `Task ${id} not found` }],
        isError: true,
      };
    }
    if (title !== undefined) task.title = title;
    if (description !== undefined) task.description = description;
    if (status !== undefined) task.status = status;
    if (priority !== undefined) task.priority = priority;
    task.updatedAt = now();
    return {
      content: [{ type: "text", text: JSON.stringify(task, null, 2) }],
    };
  }
);

server.registerTool(
  "delete_task",
  {
    description: "Permanently delete a task by ID",
    annotations: { destructiveHint: true, idempotentHint: true, openWorldHint: false },
    inputSchema: {
      id: z.string().describe("Task ID to delete"),
    },
  },
  async ({ id }) => {
    const existed = tasks.delete(id);
    return {
      content: [
        {
          type: "text",
          text: existed
            ? `Task ${id} deleted successfully`
            : `Task ${id} not found`,
        },
      ],
    };
  }
);

// --- Analytics group ---

server.registerTool(
  "get_task_summary",
  {
    description: "Get aggregate task counts grouped by status and priority",
    annotations: { readOnlyHint: true, idempotentHint: true, openWorldHint: false },
  },
  async () => {
    const allTasks = Array.from(tasks.values());
    const summary = {
      total: allTasks.length,
      byStatus: {
        todo: allTasks.filter((t) => t.status === "todo").length,
        in_progress: allTasks.filter((t) => t.status === "in_progress").length,
        done: allTasks.filter((t) => t.status === "done").length,
      },
      byPriority: {
        low: allTasks.filter((t) => t.priority === "low").length,
        medium: allTasks.filter((t) => t.priority === "medium").length,
        high: allTasks.filter((t) => t.priority === "high").length,
      },
    };
    return {
      content: [{ type: "text", text: JSON.stringify(summary, null, 2) }],
    };
  }
);

// --- Resource ---

server.registerResource(
  "task-summary",
  "tasks://summary",
  { mimeType: "application/json" },
  async () => ({
    contents: [
      {
        uri: "tasks://summary",
        text: JSON.stringify({
          total: tasks.size,
          byStatus: {
            todo: Array.from(tasks.values()).filter((t) => t.status === "todo")
              .length,
            in_progress: Array.from(tasks.values()).filter(
              (t) => t.status === "in_progress"
            ).length,
            done: Array.from(tasks.values()).filter((t) => t.status === "done")
              .length,
          },
        }),
        mimeType: "application/json",
      },
    ],
  })
);

// --- Prompt ---

server.registerPrompt(
  "task_report",
  { description: "Generate a task status report for the current sprint" },
  async () => ({
    messages: [
      {
        role: "user" as const,
        content: {
          type: "text" as const,
          text: [
            "Generate a concise status report for these tasks:",
            "",
            JSON.stringify(Array.from(tasks.values()), null, 2),
            "",
            "Include: summary stats, blockers, and next steps.",
          ].join("\n"),
        },
      },
    ],
  })
);

// ---------------------------------------------------------------------------
// mcpspec wrapper — one line to get docs + spec endpoints
// ---------------------------------------------------------------------------

const app = mcpspec(server, {
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
// Start server
// ---------------------------------------------------------------------------

const PORT = process.env.PORT ? parseInt(process.env.PORT, 10) : 3000;

app.listen(PORT, () => {
  console.log(`Task Manager MCP server running at http://localhost:${PORT}`);
  console.log(`  Docs:  http://localhost:${PORT}/docs`);
  console.log(`  Spec:  http://localhost:${PORT}/mcpspec.yaml`);
  console.log(`  MCP:   http://localhost:${PORT}/mcp`);
});
