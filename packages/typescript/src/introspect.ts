import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";

export interface IntrospectionTool {
  name: string;
  title?: string;
  description?: string;
  annotations?: Record<string, unknown>;
  inputSchema?: Record<string, unknown>;
  outputSchema?: Record<string, unknown>;
}

export interface IntrospectionResource {
  uri: string;
  name?: string;
  description?: string;
  mimeType?: string;
}

export interface IntrospectionPrompt {
  name: string;
  description?: string;
  arguments?: IntrospectionPromptArgument[];
}

export interface IntrospectionPromptArgument {
  name: string;
  description?: string;
  required?: boolean;
}

export interface IntrospectionResult {
  tools: IntrospectionTool[];
  resources: IntrospectionResource[];
  prompts: IntrospectionPrompt[];
  capabilities: Record<string, Record<string, unknown> | object>;
}

export async function introspect(
  server: McpServer,
): Promise<IntrospectionResult> {
  const [clientTransport, serverTransport] =
    InMemoryTransport.createLinkedPair();

  const client = new Client({
    name: "mcpspec-introspector",
    version: "0.1.0",
  });

  try {
    await server.connect(serverTransport);
    await client.connect(clientTransport);

    const rawCapabilities = client.getServerCapabilities() ?? {};
    const capabilities = extractCapabilities(rawCapabilities);
    const tools = rawCapabilities.tools
      ? await listAllTools(client)
      : [];
    const resources = rawCapabilities.resources
      ? await listAllResources(client)
      : [];
    const prompts = rawCapabilities.prompts
      ? await listAllPrompts(client)
      : [];

    return { tools, resources, prompts, capabilities };
  } finally {
    await client.close().catch(() => {});
    await serverTransport.close().catch(() => {});
    await clientTransport.close().catch(() => {});
  }
}

function extractCapabilities(
  raw: Record<string, unknown>,
): Record<string, Record<string, unknown> | object> {
  const result: Record<string, Record<string, unknown> | object> = {};
  for (const [key, value] of Object.entries(raw)) {
    if (typeof value === "object" && value !== null) {
      result[key] = value as Record<string, unknown>;
    } else if (value !== undefined) {
      result[key] = {};
    }
  }
  return result;
}

async function listAllTools(
  client: Client,
): Promise<IntrospectionTool[]> {
  const tools: IntrospectionTool[] = [];
  let cursor: string | undefined;

  do {
    const response = await client.listTools(
      cursor ? { cursor } : undefined,
    );
    for (const tool of response.tools) {
      tools.push({
        name: tool.name,
        title: tool.title,
        description: tool.description,
        annotations: tool.annotations as
          | Record<string, unknown>
          | undefined,
        inputSchema: tool.inputSchema as Record<string, unknown>,
        outputSchema: tool.outputSchema as
          | Record<string, unknown>
          | undefined,
      });
    }
    cursor = response.nextCursor;
  } while (cursor);

  return tools;
}

async function listAllResources(
  client: Client,
): Promise<IntrospectionResource[]> {
  const resources: IntrospectionResource[] = [];
  let cursor: string | undefined;

  do {
    const response = await client.listResources(
      cursor ? { cursor } : undefined,
    );
    for (const resource of response.resources) {
      resources.push({
        uri: resource.uri,
        name: resource.name,
        description: resource.description,
        mimeType: resource.mimeType,
      });
    }
    cursor = response.nextCursor;
  } while (cursor);

  return resources;
}

async function listAllPrompts(
  client: Client,
): Promise<IntrospectionPrompt[]> {
  const prompts: IntrospectionPrompt[] = [];
  let cursor: string | undefined;

  do {
    const response = await client.listPrompts(
      cursor ? { cursor } : undefined,
    );
    for (const prompt of response.prompts) {
      prompts.push({
        name: prompt.name,
        description: prompt.description,
        arguments: prompt.arguments?.map((arg) => ({
          name: arg.name,
          description: arg.description,
          required: arg.required,
        })),
      });
    }
    cursor = response.nextCursor;
  } while (cursor);

  return prompts;
}
