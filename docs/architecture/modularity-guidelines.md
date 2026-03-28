# Modularity Guidelines

## Module Architecture

mcpspec is organized into focused modules, each with a single responsibility. Modules communicate through well-defined TypeScript interfaces, never through shared mutable state.

### Module Map (TypeScript)

```
src/
  types.ts          — Type definitions and interfaces for the spec format
  introspect.ts     — Connects to MCP server, calls list endpoints, returns raw data
  filter.ts         — Applies include/exclude patterns and overrides to introspected data
  generate.ts       — Transforms filtered data into mcpspec.yaml structure
  serve.ts          — HTTP route handlers for /docs and /mcpspec.yaml
  mcpspec.ts        — Public API: the mcpspec() wrapper function (returns http.Server)
  cli.ts            — CLI entry point for offline spec generation
```

### Data Flow

```
McpServer instance
    → introspect.ts   (calls tools/list, resources/list, prompts/list)
    → filter.ts       (applies include/exclude/overrides)
    → generate.ts     (produces McpSpec YAML structure)
    → serve.ts        (renders HTML or YAML, serves via raw Node.js http)
```

Each arrow represents a function call with typed input and output. No module reaches into another module's internals.

## Module Rules

### Single Responsibility

Each module does ONE thing:

| Module | Responsibility | Does NOT do |
|--------|---------------|-------------|
| `types.ts` | Define interfaces and types | Any logic |
| `introspect.ts` | Connect and call MCP list endpoints | Filter, format, or serve |
| `filter.ts` | Apply include/exclude/override rules | Connect to servers or generate output |
| `generate.ts` | Transform data into spec structure | IO, HTTP, or MCP calls |
| `serve.ts` | HTTP routes and response formatting via raw Node.js `http` | Introspection or spec logic |
| `mcpspec.ts` | Wire everything together, return `http.Server` | Low-level implementation details |
| `cli.ts` | Parse CLI args, orchestrate offline generation | Serve HTTP or manage state |

### File Size Limits

- **300 lines of code maximum** per production file (excluding blank lines and comments)
- **50 lines of code maximum** per function
- If a module approaches 300 LOC, identify sub-responsibilities and extract a new module
- Test files are exempt from line limits but should be organized into focused `describe` blocks

### Interface Boundaries

Modules communicate through interfaces defined in `types.ts`:

```typescript
// Example: introspect.ts exports a function with this signature
function introspectServer(server: McpServerLike): Promise<IntrospectionResult>

// Example: filter.ts exports a function with this signature
function filterCapabilities(
  data: IntrospectionResult,
  options: FilterOptions
): FilteredCapabilities

// Example: generate.ts exports a function with this signature
function generateSpec(
  capabilities: FilteredCapabilities,
  info: McpSpecInfo
): McpSpecDocument
```

Each function takes typed input and returns typed output. No function mutates its input.

### No Shared Mutable State

- No module-level `let` variables that are mutated at runtime
- Caching is handled by `mcpspec.ts` (the orchestrator), not by individual modules
- Each function call is pure: same input produces same output (except `introspect`, which does IO)

## Error Handling

### Typed Errors

Define specific error classes for each failure mode:

```typescript
class IntrospectionError extends Error {
  constructor(
    message: string,
    readonly method: string,
    readonly cause?: Error
  ) {
    super(`Introspection failed for ${method}: ${message}`);
    this.name = 'IntrospectionError';
  }
}

class SpecGenerationError extends Error {
  constructor(
    message: string,
    readonly cause?: Error
  ) {
    super(`Spec generation failed: ${message}`);
    this.name = 'SpecGenerationError';
  }
}
```

### Error Rules

- **Never swallow errors.** Every `catch` must log, re-throw, or return a typed error.
- **Include context.** Error messages must say what failed, why, and what the user can do about it.
- **Fail gracefully for optional data.** If `resources/list` fails but `tools/list` succeeds, generate a partial spec with a warning — don't crash.
- **Fail hard for required operations.** If `initialize` or `tools/list` fails, throw — the spec cannot be generated without tools.

## Performance

### Lazy Introspection

- Do NOT introspect at server startup
- Introspect on first request to `/docs` or `/mcpspec.yaml`
- Cache the result until `notifications/tools/list_changed` is received (post-v1)

### Caching

- The generated spec is cached after first introspection
- Cache is invalidated when the server signals changes (post-v1: `ToolListChanged`)
- The HTML page is generated once from the cached spec, then served from memory
- No disk caching — everything is in-memory for simplicity

### Hot Path

The `/docs` and `/mcpspec.yaml` endpoints are the hot path after initial generation:

- Serve cached HTML/YAML directly — no re-generation per request
- No blocking operations on the hot path
- No synchronous file reads on the hot path
- Introspection (the slow part) only happens once (or on cache invalidation)

## Testing Each Module

Each module has its own test file that tests it in isolation:

| Module | Test File | Test Strategy |
|--------|-----------|---------------|
| `introspect.ts` | `introspect.test.ts` | Real MCP server with InMemoryTransport |
| `filter.ts` | `filter.test.ts` | Pure function tests with fixture data |
| `generate.ts` | `generate.test.ts` | Pure function tests with fixture data |
| `serve.ts` | `serve.test.ts` | Raw http on port 0 |
| `mcpspec.ts` | `mcpspec.test.ts` | Integration test: full flow |

Tests for pure modules (filter, generate) should be fast and deterministic. Tests for IO modules (introspect, serve) use SDK test utilities and raw http servers on port 0.
