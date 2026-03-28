// mcpspec — OpenAPI-like specs for MCP servers

export type {
  McpSpec,
  McpSpecInfo,
  McpSpecAuthor,
  McpSpecTransport,
  McpSpecAuth,
  McpSpecTool,
  McpSpecToolAnnotations,
  McpSpecToolExample,
  McpSpecResource,
  McpSpecPrompt,
  McpSpecPromptArgument,
  McpSpecOptions,
  ToolOverride,
  ResourceOverride,
  PromptOverride,
} from "./types.js";

export { introspect } from "./introspect.js";
export type {
  IntrospectionResult,
  IntrospectionTool,
  IntrospectionResource,
  IntrospectionPrompt,
  IntrospectionPromptArgument,
} from "./introspect.js";

export { filterItems, matchGlob } from "./filter.js";
export type { FilterOptions } from "./filter.js";

export { generateSpec, serializeSpec } from "./generate.js";
