// ---------------------------------------------------------------------------
// mcpspec.yaml format types — these mirror the YAML structure exactly
// ---------------------------------------------------------------------------

export interface McpSpec {
  mcpspec: string;
  $schema?: string;
  info: McpSpecInfo;
  transport?: McpSpecTransport[];
  capabilities?: Record<string, Record<string, unknown> | object>;
  tools?: McpSpecTool[];
  resources?: McpSpecResource[];
  prompts?: McpSpecPrompt[];
}

export interface McpSpecInfo {
  name: string;
  version: string;
  title?: string;
  description?: string;
  serverUrl?: string;
  repository?: string;
  license?: string;
  authors?: McpSpecAuthor[];
}

export interface McpSpecAuthor {
  name: string;
  url?: string;
}

export interface McpSpecTransport {
  type: "streamable-http" | "stdio";
  url?: string;
  command?: string;
  description?: string;
  auth?: McpSpecAuth;
}

export interface McpSpecAuth {
  type: "oauth2" | "bearer" | "api-key" | "none";
  tokenUrl?: string;
  scopes?: string[];
  description?: string;
}

export interface McpSpecTool {
  name: string;
  title?: string;
  description?: string;
  group?: string;
  annotations?: McpSpecToolAnnotations;
  inputSchema?: Record<string, unknown>;
  outputSchema?: Record<string, unknown>;
  examples?: McpSpecToolExample[];
}

export interface McpSpecToolAnnotations {
  readOnlyHint?: boolean;
  destructiveHint?: boolean;
  idempotentHint?: boolean;
  openWorldHint?: boolean;
}

export interface McpSpecToolExample {
  title: string;
  input: Record<string, unknown>;
  description?: string;
}

export interface McpSpecResource {
  uri: string;
  name?: string;
  description?: string;
  mimeType?: string;
}

export interface McpSpecPrompt {
  name: string;
  description?: string;
  arguments?: McpSpecPromptArgument[];
}

export interface McpSpecPromptArgument {
  name: string;
  description?: string;
  required?: boolean;
}

// ---------------------------------------------------------------------------
// Options types — passed by the user to mcpspec()
// ---------------------------------------------------------------------------

export interface McpSpecOptions {
  info: {
    title: string;
    description?: string;
    version: string;
    repository?: string;
    license?: string;
    serverUrl?: string;
    authors?: McpSpecAuthor[];
  };
  transport?: McpSpecTransport[];
  basePath?: string;
  exclude?: string[];
  include?: string[];
  overrides?: {
    tools?: Record<string, ToolOverride>;
    resources?: Record<string, ResourceOverride>;
    prompts?: Record<string, PromptOverride>;
  };
  groups?: Record<string, string[]>;
  examples?: Record<string, McpSpecToolExample[]>;
}

export interface ToolOverride {
  description?: string;
  group?: string;
  title?: string;
}

export interface ResourceOverride {
  description?: string;
}

export interface PromptOverride {
  description?: string;
}
