import { describe, it, expect } from "vitest";
import type {
  McpSpec,
  McpSpecOptions,
  McpSpecTool,
  McpSpecResource,
  McpSpecPrompt,
} from "../src/types.js";

describe("TypeScript types", () => {
  it("McpSpec accepts a minimal valid spec", () => {
    const spec: McpSpec = {
      mcpspec: "0.1.0",
      info: { name: "test-server", version: "1.0.0" },
    };
    expect(spec.mcpspec).toBe("0.1.0");
    expect(spec.info.name).toBe("test-server");
  });

  it("McpSpec accepts a fully populated spec", () => {
    const spec: McpSpec = {
      mcpspec: "0.1.0",
      $schema: "https://mcpspec.dev/schema/0.1.0.json",
      info: {
        name: "task-manager",
        version: "2.0.0",
        title: "Task Manager",
        description: "Manages tasks",
        serverUrl: "https://example.com",
        repository: "https://github.com/example/repo",
        license: "MIT",
        authors: [{ name: "Alice", url: "https://alice.dev" }],
      },
      transport: [
        { type: "streamable-http", url: "https://example.com/mcp" },
        { type: "stdio", command: "npx task-server" },
      ],
      capabilities: { tools: {}, resources: {} },
      tools: [
        {
          name: "create_task",
          title: "Create Task",
          description: "Creates a new task",
          group: "tasks",
          annotations: { readOnlyHint: false, destructiveHint: false },
          inputSchema: { type: "object", properties: { title: { type: "string" } } },
          outputSchema: { type: "object" },
          examples: [{ title: "Basic", input: { title: "Buy milk" } }],
        },
      ],
      resources: [{ uri: "task://list", name: "Task List", mimeType: "application/json" }],
      prompts: [
        {
          name: "summarize",
          description: "Summarize tasks",
          arguments: [{ name: "format", description: "Output format", required: false }],
        },
      ],
    };
    expect(spec.tools).toHaveLength(1);
    expect(spec.resources).toHaveLength(1);
    expect(spec.prompts).toHaveLength(1);
  });

  it("McpSpecOptions accepts valid user options", () => {
    const options: McpSpecOptions = {
      info: { title: "My Server", version: "1.0.0" },
      basePath: "/api",
      exclude: ["internal_*"],
      include: ["public_*"],
      overrides: {
        tools: { create_task: { description: "Custom desc", group: "custom" } },
        resources: { "task://list": { description: "Custom" } },
        prompts: { summarize: { description: "Custom" } },
      },
      groups: { tasks: ["create_task", "delete_task"] },
      examples: { create_task: [{ title: "Example", input: { title: "Test" } }] },
    };
    expect(options.info.title).toBe("My Server");
    expect(options.exclude).toContain("internal_*");
  });

  it("McpSpecTool requires only name", () => {
    const tool: McpSpecTool = { name: "ping" };
    expect(tool.name).toBe("ping");
    expect(tool.description).toBeUndefined();
  });

  it("McpSpecResource requires only uri", () => {
    const resource: McpSpecResource = { uri: "file://readme" };
    expect(resource.uri).toBe("file://readme");
  });

  it("McpSpecPrompt requires only name", () => {
    const prompt: McpSpecPrompt = { name: "greet" };
    expect(prompt.name).toBe("greet");
  });
});
