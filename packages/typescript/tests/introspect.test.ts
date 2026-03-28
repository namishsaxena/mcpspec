import { describe, it, expect } from "vitest";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { introspect } from "../src/introspect.js";
import type { IntrospectionResult } from "../src/introspect.js";

function createTestServer(): McpServer {
  const server = new McpServer({
    name: "test-server",
    version: "1.0.0",
  });

  server.tool(
    "get_users",
    "Retrieve a list of users",
    {
      limit: z.number().optional().describe("Max users to return"),
      offset: z.number().optional().describe("Pagination offset"),
    },
    async () => ({
      content: [{ type: "text", text: "[]" }],
    }),
  );

  server.tool(
    "create_user",
    "Create a new user account",
    {
      name: z.string().describe("User full name"),
      email: z.string().email().describe("User email address"),
    },
    async () => ({
      content: [{ type: "text", text: '{"id": "123"}' }],
    }),
  );

  server.resource(
    "users-list",
    "users://list",
    { description: "List of all users", mimeType: "application/json" },
    async () => ({
      contents: [
        {
          uri: "users://list",
          text: "[]",
          mimeType: "application/json",
        },
      ],
    }),
  );

  server.prompt(
    "user_report",
    "Generate a user activity report",
    { timeframe: z.string().describe("Report timeframe") },
    async () => ({
      messages: [
        {
          role: "user",
          content: { type: "text", text: "Generate a report" },
        },
      ],
    }),
  );

  return server;
}

describe("introspect", () => {
  it("extracts tools from a McpServer with registered items", async () => {
    const server = createTestServer();
    const result: IntrospectionResult = await introspect(server);

    expect(result.tools).toHaveLength(2);

    const getUsers = result.tools.find((t) => t.name === "get_users");
    expect(getUsers).toBeDefined();
    expect(getUsers?.description).toBe("Retrieve a list of users");
    expect(getUsers?.inputSchema).toBeDefined();
    expect(getUsers?.inputSchema?.properties).toBeDefined();
  });

  it("extracts resources from a McpServer", async () => {
    const server = createTestServer();
    const result = await introspect(server);

    expect(result.resources).toHaveLength(1);

    const usersList = result.resources.find(
      (r) => r.uri === "users://list",
    );
    expect(usersList).toBeDefined();
    expect(usersList?.name).toBe("users-list");
  });

  it("extracts prompts from a McpServer", async () => {
    const server = createTestServer();
    const result = await introspect(server);

    expect(result.prompts).toHaveLength(1);

    const report = result.prompts.find((p) => p.name === "user_report");
    expect(report).toBeDefined();
    expect(report?.description).toBe(
      "Generate a user activity report",
    );
    expect(report?.arguments).toBeDefined();
    expect(report?.arguments).toHaveLength(1);
    expect(report?.arguments?.[0]?.name).toBe("timeframe");
  });

  it("extracts capabilities from a McpServer", async () => {
    const server = createTestServer();
    const result = await introspect(server);

    expect(result.capabilities).toBeDefined();
    expect(typeof result.capabilities).toBe("object");
  });

  it("handles empty server with no tools, resources, or prompts", async () => {
    const server = new McpServer({
      name: "empty-server",
      version: "0.1.0",
    });

    const result = await introspect(server);

    expect(result.tools).toHaveLength(0);
    expect(result.resources).toHaveLength(0);
    expect(result.prompts).toHaveLength(0);
    expect(result.capabilities).toBeDefined();
  });

  it("handles server with multiple tools and correct schemas", async () => {
    const server = createTestServer();
    const result = await introspect(server);

    const createUser = result.tools.find(
      (t) => t.name === "create_user",
    );
    expect(createUser).toBeDefined();
    expect(createUser?.description).toBe("Create a new user account");

    const inputProps = createUser?.inputSchema?.properties as
      | Record<string, unknown>
      | undefined;
    expect(inputProps).toBeDefined();
    expect(inputProps?.["name"]).toBeDefined();
    expect(inputProps?.["email"]).toBeDefined();
  });
});
