import { describe, it, expect, beforeAll } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";

const SCHEMA_PATH = resolve(
  import.meta.dirname,
  "../../../schema/mcpspec.schema.json",
);

describe("mcpspec.schema.json", () => {
  let validate: ReturnType<InstanceType<typeof Ajv2020>["compile"]>;

  beforeAll(() => {
    const schema = JSON.parse(readFileSync(SCHEMA_PATH, "utf-8"));
    const ajv = new Ajv2020({ strict: true });
    addFormats(ajv);
    validate = ajv.compile(schema);
  });

  // -----------------------------------------------------------------------
  // Structure
  // -----------------------------------------------------------------------

  it("is valid JSON and compiles without errors", () => {
    expect(validate).toBeDefined();
    expect(typeof validate).toBe("function");
  });

  it("has all 10 $defs", () => {
    const schema = JSON.parse(readFileSync(SCHEMA_PATH, "utf-8"));
    const expectedDefs = [
      "info", "author", "transport", "auth", "tool",
      "toolAnnotations", "toolExample", "resource", "prompt", "promptArgument",
    ];
    expect(Object.keys(schema.$defs).sort()).toEqual(expectedDefs.sort());
  });

  // -----------------------------------------------------------------------
  // Valid documents
  // -----------------------------------------------------------------------

  it("accepts a minimal valid spec", () => {
    const doc = {
      mcpspec: "0.1.0",
      info: { name: "test-server", version: "1.0.0" },
    };
    expect(validate(doc)).toBe(true);
  });

  it("accepts a spec with all top-level fields", () => {
    const doc = {
      mcpspec: "0.1.0",
      $schema: "https://mcpspec.dev/schema/0.1.0.json",
      info: {
        name: "full-server",
        version: "2.0.0",
        title: "Full Server",
        description: "A fully specified server",
        serverUrl: "https://example.com",
        repository: "https://github.com/example/repo",
        license: "MIT",
        authors: [{ name: "Alice", url: "https://alice.dev" }],
      },
      transport: [
        { type: "streamable-http", url: "https://example.com/mcp" },
        { type: "stdio", command: "npx server" },
      ],
      capabilities: { tools: {}, resources: {} },
      tools: [
        {
          name: "create_task",
          title: "Create Task",
          description: "Creates a task",
          group: "tasks",
          annotations: {
            readOnlyHint: false,
            destructiveHint: false,
            idempotentHint: false,
            openWorldHint: false,
          },
          inputSchema: { type: "object" },
          outputSchema: { type: "object" },
          examples: [{ title: "Basic", input: { title: "Buy milk" } }],
        },
      ],
      resources: [
        { uri: "task://list", name: "Task List", description: "All tasks", mimeType: "application/json" },
      ],
      prompts: [
        {
          name: "summarize",
          description: "Summarize tasks",
          arguments: [{ name: "format", description: "Output format", required: true }],
        },
      ],
    };
    expect(validate(doc)).toBe(true);
  });

  it("accepts a spec with only tools", () => {
    const doc = {
      mcpspec: "0.1.0",
      info: { name: "tools-only", version: "1.0.0" },
      tools: [{ name: "ping" }],
    };
    expect(validate(doc)).toBe(true);
  });

  it("accepts transport with auth", () => {
    const doc = {
      mcpspec: "0.1.0",
      info: { name: "auth-server", version: "1.0.0" },
      transport: [
        {
          type: "streamable-http",
          url: "https://example.com/mcp",
          auth: { type: "oauth2", tokenUrl: "https://auth.example.com/token", scopes: ["read", "write"] },
        },
      ],
    };
    expect(validate(doc)).toBe(true);
  });

  // -----------------------------------------------------------------------
  // Invalid documents
  // -----------------------------------------------------------------------

  it("rejects a doc missing mcpspec version", () => {
    const doc = { info: { name: "test", version: "1.0.0" } };
    expect(validate(doc)).toBe(false);
  });

  it("rejects a doc missing info", () => {
    const doc = { mcpspec: "0.1.0" };
    expect(validate(doc)).toBe(false);
  });

  it("rejects info missing name", () => {
    const doc = {
      mcpspec: "0.1.0",
      info: { version: "1.0.0" },
    };
    expect(validate(doc)).toBe(false);
  });

  it("rejects info missing version", () => {
    const doc = {
      mcpspec: "0.1.0",
      info: { name: "test" },
    };
    expect(validate(doc)).toBe(false);
  });

  it("rejects invalid mcpspec version format", () => {
    const doc = {
      mcpspec: "v1",
      info: { name: "test", version: "1.0.0" },
    };
    expect(validate(doc)).toBe(false);
  });

  it("rejects unknown top-level properties", () => {
    const doc = {
      mcpspec: "0.1.0",
      info: { name: "test", version: "1.0.0" },
      unknown: true,
    };
    expect(validate(doc)).toBe(false);
  });

  it("rejects tool missing name", () => {
    const doc = {
      mcpspec: "0.1.0",
      info: { name: "test", version: "1.0.0" },
      tools: [{ description: "no name" }],
    };
    expect(validate(doc)).toBe(false);
  });

  it("rejects resource missing uri", () => {
    const doc = {
      mcpspec: "0.1.0",
      info: { name: "test", version: "1.0.0" },
      resources: [{ name: "no-uri" }],
    };
    expect(validate(doc)).toBe(false);
  });

  it("rejects prompt missing name", () => {
    const doc = {
      mcpspec: "0.1.0",
      info: { name: "test", version: "1.0.0" },
      prompts: [{ description: "no name" }],
    };
    expect(validate(doc)).toBe(false);
  });

  it("rejects invalid transport type", () => {
    const doc = {
      mcpspec: "0.1.0",
      info: { name: "test", version: "1.0.0" },
      transport: [{ type: "websocket" }],
    };
    expect(validate(doc)).toBe(false);
  });

  it("rejects invalid auth type", () => {
    const doc = {
      mcpspec: "0.1.0",
      info: { name: "test", version: "1.0.0" },
      transport: [{ type: "streamable-http", auth: { type: "basic" } }],
    };
    expect(validate(doc)).toBe(false);
  });
});
