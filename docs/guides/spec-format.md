# mcpspec.yaml Format Reference

The `mcpspec.yaml` file is a standardized description of an MCP server's capabilities. It's the MCP equivalent of an OpenAPI spec.

## Format version

Current version: `0.1.0`

```yaml
mcpspec: 0.1.0
$schema: "https://mcpspec.dev/schema/0.1.0.json"
```

The `$schema` field enables IDE validation and autocomplete for editors that support JSON Schema over YAML.

## Full annotated example

```yaml
mcpspec: 0.1.0
$schema: "https://mcpspec.dev/schema/0.1.0.json"

# --- Server metadata (author-provided) ---
info:
  name: task-manager               # Machine-readable name (from MCP server config)
  version: "1.0.0"                 # Server version
  title: Task Manager              # Human-friendly display name
  description: |                   # Multi-line description
    A task management MCP server
    for demonstration purposes.
  serverUrl: https://tasks.example.com
  repository: https://github.com/user/mcpspec
  license: MIT
  authors:
    - name: Jane Doe
      url: https://github.com/janedoe

# --- Connection methods (author-provided) ---
transport:
  - type: streamable-http
    url: https://tasks.example.com/mcp
    description: Primary HTTP endpoint for remote clients
    auth:
      type: bearer
      description: Use your API key from the dashboard
  - type: stdio
    command: npx @example/task-manager
    description: Local transport for CLI and desktop clients

# --- Server capabilities (auto-generated from MCP protocol) ---
capabilities:
  tools:
    listChanged: true
  resources:
    subscribe: false
  prompts: {}

# --- Tools (auto-generated, enriched with groups/examples) ---
tools:
  - name: create_task
    title: Create Task
    description: Create a new task with title and description
    group: Tasks                   # Author-provided via groups option
    annotations:                   # From MCP tool annotations
      readOnlyHint: false
      destructiveHint: false
      idempotentHint: false
      openWorldHint: false
    inputSchema:                   # From MCP tool definition
      type: object
      properties:
        title:
          type: string
          description: Task title
        description:
          type: string
          description: Optional description
      required:
        - title
    outputSchema:                  # From MCP tool definition (if present)
      type: object
      properties:
        id:
          type: string
        status:
          type: string
    examples:                      # Author-provided via examples option
      - title: Create a simple task
        input:
          title: Buy groceries
          description: Milk, eggs, bread
        description: Creates a new task with default settings

  - name: get_task_summary
    description: Get task counts by status
    group: Analytics
    annotations:
      readOnlyHint: true
      idempotentHint: true
    inputSchema:
      type: object
      properties: {}

# --- Resources (auto-generated) ---
resources:
  - uri: "tasks://summary"
    name: Task Summary
    description: Overall task statistics
    mimeType: application/json

# --- Prompts (auto-generated) ---
prompts:
  - name: task_report
    description: Generate a task status report
    arguments:
      - name: format
        description: Output format
        required: false
```

## Section reference

### `mcpspec` (required)

Format version string. Currently `"0.1.0"`.

### `$schema` (optional)

URL to the JSON Schema for this format version. Enables editor validation.

### `info` (required)

Server metadata. `name` and `version` are required; all other fields are optional.

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| `name` | string | Auto/author | Server name (from McpServer config or options) |
| `version` | string | Author | Server version |
| `title` | string | Author | Human-friendly display name |
| `description` | string | Author | Server description |
| `serverUrl` | string | Author | Canonical production URL |
| `repository` | string | Author | Source code repository URL |
| `license` | string | Author | SPDX license identifier |
| `authors` | array | Author | List of `{ name, url? }` objects |

### `transport` (optional)

Documents how clients connect. Purely informational.

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"streamable-http"` or `"stdio"` | Transport type |
| `url` | string | Server URL (for streamable-http) |
| `command` | string | CLI command (for stdio) |
| `description` | string | Human-readable description of this transport |
| `auth` | object | Auth requirements (per-transport) |
| `auth.type` | `"oauth2"`, `"bearer"`, `"api-key"`, `"none"` | Auth mechanism |
| `auth.tokenUrl` | string | OAuth2 token endpoint |
| `auth.scopes` | string[] | OAuth2 scopes |
| `auth.description` | string | Human-readable description of auth requirements |

### `capabilities` (auto-generated)

Server capabilities as reported by the MCP protocol during initialization. Reflects what the server supports (tool list change notifications, resource subscriptions, etc.).

### `tools` (auto-generated + enriched)

Array of tool definitions.

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| `name` | string | Auto | Tool name from MCP registration |
| `title` | string | Auto/override | Display title |
| `description` | string | Auto/override | Tool description |
| `group` | string | Author | Group name (from `groups` option) |
| `annotations` | object | Auto | MCP tool annotations |
| `inputSchema` | object | Auto | JSON Schema for tool input |
| `outputSchema` | object | Auto | JSON Schema for tool output (if defined) |
| `examples` | array | Author | Usage examples (from `examples` option) |

### `resources` (auto-generated)

Array of resource definitions.

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| `uri` | string | Auto | Resource URI pattern |
| `name` | string | Auto | Display name |
| `description` | string | Auto/override | Resource description |
| `mimeType` | string | Auto | Content type |

### `prompts` (auto-generated)

Array of prompt definitions.

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| `name` | string | Auto | Prompt name |
| `description` | string | Auto/override | Prompt description |
| `arguments` | array | Auto | List of `{ name, description?, required? }` objects |

## Auto-generated vs author-enriched

| Source | Fields |
|--------|--------|
| **Auto-generated** (from MCP protocol, zero config) | Tool names/descriptions/schemas/annotations, resource URIs/names/descriptions/mimeTypes, prompt names/descriptions/arguments, capabilities |
| **Author-enriched** (via options) | info block, transport block, groups, examples, overrides, exclude/include filtering |

## JSON Schema validation

Validate any `mcpspec.yaml` file against the JSON Schema:

```bash
# Using ajv-cli
npx ajv validate -s https://mcpspec.dev/schema/0.1.0.json -d mcpspec.yaml
```

The schema is also available in the repository at `schema/mcpspec.schema.json`.
