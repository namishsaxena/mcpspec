import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import type { IncomingMessage, ServerResponse } from "node:http";
import type { McpSpec } from "./types.js";
import { serializeSpec } from "./generate.js";

const currentDir = dirname(fileURLToPath(import.meta.url));

function loadDocsTemplate(): string {
  try {
    return readFileSync(join(currentDir, "ui/docs.html"), "utf-8");
  } catch {
    return "<!DOCTYPE html><html><head><title>__TITLE__</title></head><body><pre>__SPEC_DATA__</pre></body></html>";
  }
}

const docsTemplate = loadDocsTemplate();

function buildDocsHtml(spec: McpSpec): string {
  const title = spec.info?.title ?? spec.info?.name ?? "MCP Server";
  return docsTemplate
    .replace("__SPEC_DATA__", JSON.stringify(spec))
    .replace("__TITLE__", title);
}

export interface HandleRequestOptions {
  getSpec: () => McpSpec | null;
  basePath?: string;
}

/**
 * Route handler for mcpspec's built-in routes (/docs, /mcpspec.yaml).
 * Designed to be called from an http.Server request listener.
 * Returns `true` if the request was handled, `false` if it was not
 * a recognized route (caller can then respond with 404 or delegate).
 */
export function handleRequest(
  req: IncomingMessage,
  res: ServerResponse,
  options: HandleRequestOptions,
): boolean {
  const prefix = (options.basePath ?? "").replace(/\/$/, "");
  const url = req.url ?? "/";

  if (req.method === "GET" && url === `${prefix}/docs`) {
    return serveDocs(res, options.getSpec);
  }

  if (req.method === "GET" && url === `${prefix}/mcpspec.yaml`) {
    return serveYaml(res, options.getSpec);
  }

  res.writeHead(404, { "content-type": "text/plain; charset=utf-8" });
  res.end("Not Found");
  return false;
}

function serveDocs(
  res: ServerResponse,
  getSpec: () => McpSpec | null,
): boolean {
  const spec = getSpec();
  if (!spec) {
    res.writeHead(503, { "content-type": "text/plain; charset=utf-8" });
    res.end("Spec not yet available. Server is still initializing.");
    return true;
  }
  const html = buildDocsHtml(spec);
  res.writeHead(200, { "content-type": "text/html; charset=utf-8" });
  res.end(html);
  return true;
}

function serveYaml(
  res: ServerResponse,
  getSpec: () => McpSpec | null,
): boolean {
  const spec = getSpec();
  if (!spec) {
    res.writeHead(503, { "content-type": "text/plain; charset=utf-8" });
    res.end("Spec not yet available. Server is still initializing.");
    return true;
  }
  res.writeHead(200, { "content-type": "text/yaml; charset=utf-8" });
  res.end(serializeSpec(spec));
  return true;
}
