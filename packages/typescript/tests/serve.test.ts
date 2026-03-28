import http from "node:http";
import { describe, it, expect, afterEach } from "vitest";
import { handleRequest } from "../src/serve.js";
import type { McpSpec } from "../src/types.js";

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

function startServer(
  getSpec: () => McpSpec | null,
  basePath = "",
): Promise<http.Server> {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      handleRequest(req, res, { getSpec, basePath });
    });
    server.listen(0, "127.0.0.1", () => resolve(server));
  });
}

function closeServer(server: http.Server): Promise<void> {
  return new Promise((resolve) => {
    server.close(() => resolve());
  });
}

describe("handleRequest", () => {
  const servers: http.Server[] = [];

  const mockSpec: McpSpec = {
    mcpspec: "0.1.0",
    info: { name: "Test", version: "1.0.0", title: "Test Server" },
    tools: [
      {
        name: "test_tool",
        description: "A test tool",
        inputSchema: { type: "object" },
      },
    ],
    resources: [],
    prompts: [],
  };

  afterEach(async () => {
    for (const server of servers) {
      await closeServer(server);
    }
    servers.length = 0;
  });

  it("serves HTML at /docs with correct content-type", async () => {
    const server = await startServer(() => mockSpec);
    servers.push(server);

    const response = await makeRequest(server, "/docs");

    expect(response.status).toBe(200);
    expect(response.headers["content-type"]).toContain("text/html");
    expect(response.body).toContain("Test Server");
    expect(response.body).toContain("test_tool");
  });

  it("serves YAML at /mcpspec.yaml with correct content-type", async () => {
    const server = await startServer(() => mockSpec);
    servers.push(server);

    const response = await makeRequest(server, "/mcpspec.yaml");

    expect(response.status).toBe(200);
    expect(response.headers["content-type"]).toContain("text/yaml");
    expect(response.body).toContain("mcpspec:");
    expect(response.body).toContain("test_tool");
  });

  it("supports basePath prefix", async () => {
    const server = await startServer(() => mockSpec, "/api/v1");
    servers.push(server);

    const docsResponse = await makeRequest(server, "/api/v1/docs");
    expect(docsResponse.status).toBe(200);
    expect(docsResponse.body).toContain("Test Server");

    const yamlResponse = await makeRequest(server, "/api/v1/mcpspec.yaml");
    expect(yamlResponse.status).toBe(200);
    expect(yamlResponse.body).toContain("mcpspec:");
  });

  it("returns 503 when spec is null", async () => {
    const server = await startServer(() => null);
    servers.push(server);

    const docsResponse = await makeRequest(server, "/docs");
    expect(docsResponse.status).toBe(503);

    const yamlResponse = await makeRequest(server, "/mcpspec.yaml");
    expect(yamlResponse.status).toBe(503);
  });

  it("strips trailing slash from basePath", async () => {
    const server = await startServer(() => mockSpec, "/prefix/");
    servers.push(server);

    const response = await makeRequest(server, "/prefix/docs");
    expect(response.status).toBe(200);
  });

  it("returns 404 for unknown routes", async () => {
    const server = await startServer(() => mockSpec);
    servers.push(server);

    const response = await makeRequest(server, "/unknown");
    expect(response.status).toBe(404);
  });

  it("HTML contains spec data as JSON for client-side rendering", async () => {
    const server = await startServer(() => mockSpec);
    servers.push(server);

    const response = await makeRequest(server, "/docs");

    expect(response.body).toContain('"mcpspec":"0.1.0"');
    expect(response.body).toContain('"name":"test_tool"');
  });

  it("HTML title is set from spec info", async () => {
    const server = await startServer(() => mockSpec);
    servers.push(server);

    const response = await makeRequest(server, "/docs");

    expect(response.body).toContain("<title>Test Server");
  });
});
