# Coding Standards

## TypeScript

### Compiler Configuration

- Strict mode: `"strict": true` in tsconfig.json
- ESM only: `"type": "module"` in package.json, `.js` extensions in imports
- Target: ES2022 or later
- Module: NodeNext
- No implicit any, no unused locals, no unused parameters

### Language Rules

- **No `any`** in production code. Use `unknown` and narrow with type guards.
- **No `enum`**. Use `as const` objects or union types instead.
- **No default exports**. Use named exports exclusively.
- **Explicit return types** on all exported functions.
- **Prefer `interface`** for object shapes that may be extended. Use `type` for unions, intersections, and mapped types.
- **Prefer `readonly`** for properties that should not be mutated after construction.
- **Prefer `const` assertions** (`as const`) for literal types.
- **No classes** unless modeling stateful objects with clear lifecycle. Prefer plain functions and interfaces.

### Import Rules

- Always use `.js` extension in relative imports (ESM requirement)
- Group imports: node builtins, external packages, internal modules (blank line between groups)
- No circular imports
- No `import *`

### Error Handling

- Use typed error classes that extend `Error`
- Never swallow errors silently (`catch (e) {}`)
- Always include context in error messages: what failed, why, and what to do
- Use `Result<T, E>` patterns for expected failures (validation, parsing)

### Async

- Prefer `async/await` over raw Promises
- Never use `.then()` chains when `await` is available
- Always handle Promise rejections

## Python (Phase 2)

### Version and Runtime

- Python 3.11+ required
- Type hints on all function signatures and return types
- Pydantic for data models and validation

### Linting and Formatting

- Ruff for linting and formatting (replaces Black, isort, flake8)
- All Ruff defaults plus strict type checking rules

### Language Rules

- No `from module import *`
- No mutable default arguments
- Dataclasses or Pydantic models, not plain dicts for structured data
- Type narrowing with `isinstance()` or `TypeGuard`
- `pathlib.Path` over `os.path`

## Naming Conventions

### TypeScript

| Entity | Convention | Example |
|--------|-----------|---------|
| Files | kebab-case | `introspect-server.ts` |
| Test files | `{module}.test.ts` | `introspect.test.ts` |
| Interfaces | PascalCase | `McpSpecConfig` |
| Types | PascalCase | `ToolDefinition` |
| Functions | camelCase | `introspectServer` |
| Constants | SCREAMING_SNAKE | `DEFAULT_PORT` |
| Variables | camelCase | `toolCount` |
| Boolean variables | `is`/`has`/`should` prefix | `isReady`, `hasTools` |

### Python

| Entity | Convention | Example |
|--------|-----------|---------|
| Files | snake_case | `introspect_server.py` |
| Test files | `test_{module}.py` | `test_introspect.py` |
| Classes | PascalCase | `McpSpec` |
| Functions | snake_case | `introspect_server` |
| Constants | SCREAMING_SNAKE | `DEFAULT_PORT` |
| Variables | snake_case | `tool_count` |
| Private | `_` prefix | `_internal_cache` |

## Documentation

- All exported functions must have JSDoc (TypeScript) or docstrings (Python)
- JSDoc must include `@param` and `@returns` tags
- Keep comments to "why", not "what" — the code should be readable without comments
- TODO and FIXME comments must include a linked issue: `// TODO(#42): refactor when SDK supports streaming`
- Update docs when behavior changes
