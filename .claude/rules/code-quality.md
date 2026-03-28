---
description: Core code quality standards for mcpspec
alwaysApply: true
---

# Code Quality Rules

## Single Responsibility

- One function does one thing. If you need "and" to describe it, split it.
- One module has one reason to change.

## No Magic Values

- Use named constants for any literal value that has meaning.
- Exception: `0`, `1`, `true`, `false`, empty string `""`, and empty array `[]` are acceptable inline.

## Naming Conventions

- **PascalCase**: types, interfaces, classes (`McpSpec`, `ToolDefinition`, `ServerCapabilities`)
- **camelCase**: functions, variables, parameters (`introspectServer`, `toolCount`, `filterOptions`)
- **SCREAMING_SNAKE_CASE**: constants (`DEFAULT_PORT`, `MAX_TOOLS`, `MCP_SPEC_VERSION`)
- **kebab-case**: file names (`introspect-server.ts`, `filter-options.ts`, `serve-docs.ts`)

## Boolean Naming

- Prefix with: `is`, `has`, `should`, `can`
- Examples: `isReady`, `hasResources`, `shouldPaginate`, `canFilter`

## Function Clarity

- If the intent of a code block isn't clear from reading, extract it into a named function.
- The function name should explain the "what". Comments should explain the "why".

## Abstraction Timing

- Do NOT extract a shared abstraction until you have 3+ concrete usages.
- Premature abstraction is harder to undo than duplication.

## Comments

- Comments explain "why", code explains "what".
- Do not comment obvious code. Do comment non-obvious decisions, workarounds, and constraints.
