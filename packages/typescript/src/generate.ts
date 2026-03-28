import yaml from "js-yaml";
import { filterItems } from "./filter.js";
import type { FilterOptions } from "./filter.js";
import type { IntrospectionResult } from "./introspect.js";
import type {
  McpSpec,
  McpSpecOptions,
  McpSpecTool,
  McpSpecToolAnnotations,
  McpSpecResource,
  McpSpecPrompt,
} from "./types.js";

const MCPSPEC_VERSION = "0.1.0";
const SCHEMA_URL = `https://mcpspec.dev/schema/${MCPSPEC_VERSION}.json`;

export function generateSpec(
  introspection: IntrospectionResult,
  options: McpSpecOptions,
): McpSpec {
  const filterOpts: FilterOptions = {
    include: options.include,
    exclude: options.exclude,
  };

  const filteredTools = filterItems(introspection.tools, filterOpts);
  const filteredResources = filterItems(
    introspection.resources.map((r) => ({ ...r, name: r.name ?? r.uri })),
    filterOpts,
  );
  const filteredPrompts = filterItems(introspection.prompts, filterOpts);

  const tools = filteredTools.map((tool) => mapTool(tool, options));
  const resources = filteredResources.map((resource) =>
    mapResource(resource, options),
  );
  const prompts = filteredPrompts.map((prompt) => mapPrompt(prompt, options));

  const spec: McpSpec = {
    mcpspec: MCPSPEC_VERSION,
    $schema: SCHEMA_URL,
    info: {
      name: titleToSlug(options.info.title),
      version: options.info.version,
      title: options.info.title,
      description: options.info.description,
      serverUrl: options.info.serverUrl,
      repository: options.info.repository,
      license: options.info.license,
      authors: options.info.authors,
    },
    capabilities: introspection.capabilities,
    tools,
    resources,
    prompts,
  };

  if (options.transport && options.transport.length > 0) {
    spec.transport = options.transport;
  }

  return cleanUndefined(spec);
}

export function serializeSpec(spec: McpSpec): string {
  return yaml.dump(spec, {
    indent: 2,
    lineWidth: 120,
    noRefs: true,
    sortKeys: false,
    quotingType: '"',
    forceQuotes: false,
  });
}

function mapTool(
  tool: {
    name: string;
    title?: string;
    description?: string;
    annotations?: Record<string, unknown>;
    inputSchema?: Record<string, unknown>;
    outputSchema?: Record<string, unknown>;
  },
  options: McpSpecOptions,
): McpSpecTool {
  const override = options.overrides?.tools?.[tool.name];
  const groupFromGroups = findGroup(tool.name, options.groups);
  const examples = options.examples?.[tool.name];

  const result: McpSpecTool = {
    name: tool.name,
    title: override?.title ?? tool.title,
    description: override?.description ?? tool.description,
    group: override?.group ?? groupFromGroups,
    annotations: mapAnnotations(tool.annotations),
    inputSchema: tool.inputSchema,
    outputSchema: tool.outputSchema,
    examples: examples,
  };

  return cleanUndefined(result);
}

function mapResource(
  resource: {
    uri: string;
    name?: string;
    description?: string;
    mimeType?: string;
  },
  options: McpSpecOptions,
): McpSpecResource {
  const override =
    options.overrides?.resources?.[resource.name ?? resource.uri];

  const result: McpSpecResource = {
    uri: resource.uri,
    name: resource.name,
    description: override?.description ?? resource.description,
    mimeType: resource.mimeType,
  };

  return cleanUndefined(result);
}

function mapPrompt(
  prompt: {
    name: string;
    description?: string;
    arguments?: Array<{
      name: string;
      description?: string;
      required?: boolean;
    }>;
  },
  options: McpSpecOptions,
): McpSpecPrompt {
  const override = options.overrides?.prompts?.[prompt.name];

  const result: McpSpecPrompt = {
    name: prompt.name,
    description: override?.description ?? prompt.description,
    arguments: prompt.arguments?.map((arg) => ({
      name: arg.name,
      description: arg.description,
      required: arg.required,
    })),
  };

  return cleanUndefined(result);
}

function mapAnnotations(
  raw: Record<string, unknown> | undefined,
): McpSpecToolAnnotations | undefined {
  if (!raw) return undefined;

  const result: McpSpecToolAnnotations = {};
  if (typeof raw["readOnlyHint"] === "boolean") {
    result.readOnlyHint = raw["readOnlyHint"];
  }
  if (typeof raw["destructiveHint"] === "boolean") {
    result.destructiveHint = raw["destructiveHint"];
  }
  if (typeof raw["idempotentHint"] === "boolean") {
    result.idempotentHint = raw["idempotentHint"];
  }
  if (typeof raw["openWorldHint"] === "boolean") {
    result.openWorldHint = raw["openWorldHint"];
  }

  return Object.keys(result).length > 0 ? result : undefined;
}

function findGroup(
  toolName: string,
  groups: Record<string, string[]> | undefined,
): string | undefined {
  if (!groups) return undefined;

  for (const [groupName, toolNames] of Object.entries(groups)) {
    if (toolNames.includes(toolName)) {
      return groupName;
    }
  }
  return undefined;
}

function titleToSlug(title: string): string {
  return title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

function cleanUndefined<T extends object>(obj: T): T {
  const cleaned = { ...obj } as Record<string, unknown>;
  for (const key of Object.keys(cleaned)) {
    if (cleaned[key] === undefined) {
      delete cleaned[key];
    }
  }
  return cleaned as T;
}
