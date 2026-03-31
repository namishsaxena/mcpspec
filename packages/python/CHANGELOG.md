# Changelog

All notable changes to the Python package will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/).

## [0.1.0] - 2026-03-31

### Added
- Pydantic models for mcpspec document and options
- MCP server introspection via in-memory transport
- Glob-based include/exclude filtering for tools, resources, and prompts
- Spec generation with YAML serialization
- Starlette route handlers for /docs and /mcpspec.yaml
- McpSpec class with route injection and create_app
- Typed error classes for introspection and generation

### Fixed
- Export McpSpecAuthor from mcpspec_dev
- Make mcp a required dependency, not optional
- Template replacement order to prevent spec data corruption
- Preserve annotation values at introspection level for parity
- Preserve empty inputSchema, use identity check not truthiness
- Pagination loop bounds to prevent infinite introspection
- Preserve empty capabilities dict, matching TypeScript parity
- Override nullish semantics and accept dict overrides
- Prevent resource name mutation in generate_spec
- URL scheme validation in docs UI to prevent javascript: XSS

### Security
- Introspection-only boundary — never calls tools/call, prompts/get, or resources/read

