import http from "node:http";
import { describe, it, expect, afterEach } from "vitest";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { mcpspec, createHandler } from "../src/mcpspec.js";

function makeRequest(
  server: http.Server,
  path: string,
  method = "GET",
): Promise<{ status: number; headers: http.IncomingHttpHeaders; body: string }> {
  return new Promise((resolve, reject) => {
    const addr = server.address() as { port: number };
    const req = http.request(
      { hostname: "127.0.0.1", port: addr.port, path, method },
      (res) => {
        let body = "";
        res.on("data", (chunk: Buffer) => {
          body += chunk.toString();
        });
        res.on("end", () =>
          resolve({ status: res.statusCode!, headers: res.headers, body }),
        );
      },
    );
    req.on("error", reject);
    req.end();
  });
}

function postRequest(
  server: http.Server,
  path: string,
  payload: unknown,
): Promise<{ status: number; headers: http.IncomingHttpHeaders; body: string }> {
  return new Promise((resolve, reject) => {
    const addr = server.address() as { port: number };
    const data = JSON.stringify(payload);
    const req = http.request(
      {
        hostname: "127.0.0.1",
        port: addr.port,
        path,
        method: "POST",
        headers: {
          "content-type": "application/json",
          accept: "application/json, text/event-stream",
          "content-length": Buffer.byteLength(data),
        },
      },
      (res) => {
        let body = "";
        res.on("data", (chunk: Buffer) => {
          body += chunk.toString();
        });
        res.on("end", () =>
          resolve({ status: res.statusCode!, headers: res.headers, body }),
        );
      },
    );
    req.on("error", reject);
    req.write(data);
    req.end();
  });
}

function listenServer(server: http.Server): Promise<void> {
  return new Promise((resolve) => {
    server.listen(0, "127.0.0.1", () => resolve());
  });
}

function closeServer(server: http.Server): Promise<void> {
  return new Promise((resolve) => {
    server.close(() => resolve());
  });
}

describe("mcpspec", () => {
  const instances: http.Server[] = [];

  afterEach(async () => {
    for (const server of instances) {
      await closeServer(server);
    }
    instances.length = 0;
  });

  it("creates http.Server with /docs and /mcpspec.yaml", async () => {
    const server = new McpServer({
      name: "test-server",
      version: "1.0.0",
    });

    server.tool(
      "greet",
      "Say hello to someone",
      { name: z.string().describe("Name to greet") },
      async ({ name }) => ({
        content: [{ type: "text", text: `Hello, ${name}!` }],
      }),
    );

    const app = mcpspec(server, {
      info: {
        title: "Test Server",
        version: "1.0.0",
        description: "A test MCP server",
      },
    });
    instances.push(app);
    await listenServer(app);

    const docsResponse = await makeRequest(app, "/docs");

    expect(docsResponse.status).toBe(200);
    expect(docsResponse.headers["content-type"]).toContain("text/html");
    expect(docsResponse.body).toContain("Test Server");
    expect(docsResponse.body).toContain("greet");

    const yamlResponse = await makeRequest(app, "/mcpspec.yaml");

    expect(yamlResponse.status).toBe(200);
    expect(yamlResponse.headers["content-type"]).toContain("text/yaml");
    expect(yamlResponse.body).toContain("mcpspec:");
    expect(yamlResponse.body).toContain("greet");
    expect(yamlResponse.body).toContain("Say hello to someone");
  });

  it("/docs returns HTML containing tool names from introspection", async () => {
    const server = new McpServer({
      name: "multi-tool-server",
      version: "2.0.0",
    });

    server.tool(
      "alpha_tool",
      "First tool",
      { input: z.string() },
      async () => ({
        content: [{ type: "text", text: "alpha" }],
      }),
    );

    server.tool(
      "beta_tool",
      "Second tool",
      { input: z.string() },
      async () => ({
        content: [{ type: "text", text: "beta" }],
      }),
    );

    const app = mcpspec(server, {
      info: { title: "Multi Tool", version: "2.0.0" },
    });
    instances.push(app);
    await listenServer(app);

    const response = await makeRequest(app, "/docs");

    expect(response.body).toContain("alpha_tool");
    expect(response.body).toContain("beta_tool");
    expect(response.body).toContain("Multi Tool");
  });

  it("/mcpspec.yaml returns YAML containing spec version and tool names", async () => {
    const server = new McpServer({
      name: "yaml-test",
      version: "1.0.0",
    });

    server.tool(
      "do_something",
      "Does something useful",
      {},
      async () => ({
        content: [{ type: "text", text: "done" }],
      }),
    );

    const app = mcpspec(server, {
      info: { title: "YAML Test", version: "1.0.0" },
    });
    instances.push(app);
    await listenServer(app);

    const response = await makeRequest(app, "/mcpspec.yaml");

    expect(response.body).toContain("mcpspec: 0.1.0");
    expect(response.body).toContain("do_something");
    expect(response.body).toContain("Does something useful");
  });

  it("respects basePath option", async () => {
    const server = new McpServer({
      name: "basepath-test",
      version: "1.0.0",
    });

    const app = mcpspec(server, {
      info: { title: "BasePath Test", version: "1.0.0" },
      basePath: "/api/spec",
    });
    instances.push(app);
    await listenServer(app);

    const docsResponse = await makeRequest(app, "/api/spec/docs");
    expect(docsResponse.status).toBe(200);
    expect(docsResponse.body).toContain("BasePath Test");

    const yamlResponse = await makeRequest(app, "/api/spec/mcpspec.yaml");
    expect(yamlResponse.status).toBe(200);
    expect(yamlResponse.body).toContain("mcpspec:");
  });

  it("applies exclude filter to omit matching tools", async () => {
    const server = new McpServer({
      name: "filter-test",
      version: "1.0.0",
    });

    server.tool(
      "public_tool",
      "A public tool",
      {},
      async () => ({
        content: [{ type: "text", text: "public" }],
      }),
    );

    server.tool(
      "internal_debug",
      "An internal debug tool",
      {},
      async () => ({
        content: [{ type: "text", text: "debug" }],
      }),
    );

    const app = mcpspec(server, {
      info: { title: "Filter Test", version: "1.0.0" },
      exclude: ["internal_*"],
    });
    instances.push(app);
    await listenServer(app);

    const response = await makeRequest(app, "/mcpspec.yaml");

    expect(response.body).toContain("public_tool");
    expect(response.body).not.toContain("internal_debug");
  });

  it("applies include filter as allowlist", async () => {
    const server = new McpServer({
      name: "include-test",
      version: "1.0.0",
    });

    server.tool("allowed_tool", "Allowed", {}, async () => ({
      content: [{ type: "text", text: "ok" }],
    }));

    server.tool("blocked_tool", "Blocked", {}, async () => ({
      content: [{ type: "text", text: "ok" }],
    }));

    const app = mcpspec(server, {
      info: { title: "Include Test", version: "1.0.0" },
      include: ["allowed_*"],
    });
    instances.push(app);
    await listenServer(app);

    const response = await makeRequest(app, "/mcpspec.yaml");

    expect(response.body).toContain("allowed_tool");
    expect(response.body).not.toContain("blocked_tool");
  });

  it("caches spec after first request", async () => {
    const server = new McpServer({
      name: "cache-test",
      version: "1.0.0",
    });

    server.tool("cached_tool", "Cached", {}, async () => ({
      content: [{ type: "text", text: "ok" }],
    }));

    const app = mcpspec(server, {
      info: { title: "Cache Test", version: "1.0.0" },
    });
    instances.push(app);
    await listenServer(app);

    const first = await makeRequest(app, "/mcpspec.yaml");
    const second = await makeRequest(app, "/mcpspec.yaml");

    expect(first.status).toBe(200);
    expect(second.status).toBe(200);
    expect(first.body).toBe(second.body);
  });

  it("works with server that has no tools, resources, or prompts", async () => {
    const server = new McpServer({
      name: "empty-server",
      version: "0.1.0",
    });

    const app = mcpspec(server, {
      info: { title: "Empty Server", version: "0.1.0" },
    });
    instances.push(app);
    await listenServer(app);

    const docsResponse = await makeRequest(app, "/docs");
    expect(docsResponse.status).toBe(200);
    expect(docsResponse.body).toContain("Empty Server");

    const yamlResponse = await makeRequest(app, "/mcpspec.yaml");
    expect(yamlResponse.status).toBe(200);
    expect(yamlResponse.body).toContain("mcpspec:");
  });

  it("applies tool groups from options", async () => {
    const server = new McpServer({
      name: "groups-test",
      version: "1.0.0",
    });

    server.tool("create_task", "Create", {}, async () => ({
      content: [{ type: "text", text: "ok" }],
    }));

    server.tool("get_summary", "Summary", {}, async () => ({
      content: [{ type: "text", text: "ok" }],
    }));

    const app = mcpspec(server, {
      info: { title: "Groups Test", version: "1.0.0" },
      groups: {
        Tasks: ["create_task"],
        Analytics: ["get_summary"],
      },
    });
    instances.push(app);
    await listenServer(app);

    const response = await makeRequest(app, "/mcpspec.yaml");

    expect(response.body).toContain("group: Tasks");
    expect(response.body).toContain("group: Analytics");
  });

  it("POST /mcp returns a valid MCP JSON-RPC response", async () => {
    const server = new McpServer({
      name: "mcp-test",
      version: "1.0.0",
    });

    server.tool("ping", "Ping", {}, async () => ({
      content: [{ type: "text", text: "pong" }],
    }));

    const app = mcpspec(server, {
      info: { title: "MCP Test", version: "1.0.0" },
    });
    instances.push(app);
    await listenServer(app);

    // Send an MCP initialize request
    const response = await postRequest(app, "/mcp", {
      jsonrpc: "2.0",
      id: 1,
      method: "initialize",
      params: {
        protocolVersion: "2025-03-26",
        capabilities: {},
        clientInfo: { name: "test-client", version: "1.0.0" },
      },
    });

    expect(response.status).toBe(200);
    // The response should be valid JSON-RPC (either direct JSON or SSE)
    // With stateless mode, we expect a JSON response or SSE stream
    expect(
      response.headers["content-type"]?.includes("application/json") ||
        response.headers["content-type"]?.includes("text/event-stream"),
    ).toBe(true);
  });

  it("returns 404 for unknown routes", async () => {
    const server = new McpServer({
      name: "404-test",
      version: "1.0.0",
    });

    const app = mcpspec(server, {
      info: { title: "404 Test", version: "1.0.0" },
    });
    instances.push(app);
    await listenServer(app);

    const response = await makeRequest(app, "/nonexistent");
    expect(response.status).toBe(404);
  });
});

describe("createHandler", () => {
  const instances: http.Server[] = [];

  afterEach(async () => {
    for (const server of instances) {
      await closeServer(server);
    }
    instances.length = 0;
  });

  it("returns a request handler function", () => {
    const server = new McpServer({
      name: "handler-test",
      version: "1.0.0",
    });

    const handler = createHandler(server, {
      info: { title: "Handler Test", version: "1.0.0" },
    });

    expect(typeof handler).toBe("function");
  });

  it("serves /docs and /mcpspec.yaml when composed with http.createServer", async () => {
    const server = new McpServer({
      name: "compose-test",
      version: "1.0.0",
    });

    server.tool(
      "hello",
      "Say hello",
      { name: z.string() },
      async ({ name }) => ({
        content: [{ type: "text", text: `Hello, ${name}!` }],
      }),
    );

    const handler = createHandler(server, {
      info: { title: "Compose Test", version: "1.0.0" },
    });

    const app = http.createServer(handler);
    instances.push(app);
    await listenServer(app);

    const docsResponse = await makeRequest(app, "/docs");
    expect(docsResponse.status).toBe(200);
    expect(docsResponse.headers["content-type"]).toContain("text/html");
    expect(docsResponse.body).toContain("Compose Test");
    expect(docsResponse.body).toContain("hello");

    const yamlResponse = await makeRequest(app, "/mcpspec.yaml");
    expect(yamlResponse.status).toBe(200);
    expect(yamlResponse.headers["content-type"]).toContain("text/yaml");
    expect(yamlResponse.body).toContain("hello");
  });

  it("can be wrapped with auth middleware that blocks /mcp", async () => {
    const server = new McpServer({
      name: "auth-compose-test",
      version: "1.0.0",
    });

    server.tool("ping", "Ping", {}, async () => ({
      content: [{ type: "text", text: "pong" }],
    }));

    const handler = createHandler(server, {
      info: { title: "Auth Compose", version: "1.0.0" },
    });

    const app = http.createServer((req, res) => {
      if (req.url === "/mcp" && req.headers.authorization !== "Bearer test-token") {
        res.writeHead(401, { "www-authenticate": "Bearer" });
        res.end("Unauthorized");
        return;
      }
      handler(req, res);
    });
    instances.push(app);
    await listenServer(app);

    // /docs should be public
    const docsResponse = await makeRequest(app, "/docs");
    expect(docsResponse.status).toBe(200);

    // /mcp without token should be 401
    const mcpNoAuth = await postRequest(app, "/mcp", {
      jsonrpc: "2.0",
      id: 1,
      method: "initialize",
      params: {
        protocolVersion: "2025-03-26",
        capabilities: {},
        clientInfo: { name: "test", version: "1.0.0" },
      },
    });
    expect(mcpNoAuth.status).toBe(401);

    // /mcpspec.yaml should be public
    const yamlResponse = await makeRequest(app, "/mcpspec.yaml");
    expect(yamlResponse.status).toBe(200);
  });
});
