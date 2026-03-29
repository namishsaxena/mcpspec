import http from "node:http";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { introspect } from "./introspect.js";
import { generateSpec } from "./generate.js";
import { handleRequest } from "./serve.js";
import type { McpSpec, McpSpecOptions } from "./types.js";

export type McpSpecRequestHandler = (
  req: http.IncomingMessage,
  res: http.ServerResponse,
) => void | Promise<void>;

/**
 * Create a request handler that serves:
 *   - /docs          — human-readable HTML docs
 *   - /mcpspec.yaml  — machine-readable spec
 *   - /mcp           — MCP streamable-http endpoint
 *
 * Compose with http.createServer() or wrap with middleware.
 * Introspection is performed lazily on the first request
 * and cached for all subsequent requests.
 */
export function createHandler(
  server: McpServer,
  options: McpSpecOptions,
): McpSpecRequestHandler {
  let cachedSpec: McpSpec | null = null;
  let introspectionPromise: Promise<void> | null = null;

  async function ensureSpec(): Promise<void> {
    if (cachedSpec) return;
    if (!introspectionPromise) {
      introspectionPromise = (async () => {
        const result = await introspect(server);
        cachedSpec = generateSpec(result, options);
      })();
    }
    return introspectionPromise;
  }

  const basePath = (options.basePath ?? "").replace(/\/$/, "");

  return async (req: http.IncomingMessage, res: http.ServerResponse) => {
    const url = req.url ?? "/";

    if (url === `${basePath}/mcp`) {
      await handleMcpRoute(req, res, server);
      return;
    }

    await ensureSpec();

    handleRequest(req, res, {
      getSpec: () => cachedSpec,
      basePath,
    });
  };
}

/**
 * Create an http.Server that serves /docs, /mcpspec.yaml, and /mcp.
 * Convenience wrapper around createHandler().
 */
export function mcpspec(
  server: McpServer,
  options: McpSpecOptions,
): http.Server {
  return http.createServer(createHandler(server, options));
}

async function handleMcpRoute(
  req: http.IncomingMessage,
  res: http.ServerResponse,
  mcpServer: McpServer,
): Promise<void> {
  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: undefined,
  });

  await mcpServer.server.connect(transport);
  await transport.handleRequest(req, res);
}
