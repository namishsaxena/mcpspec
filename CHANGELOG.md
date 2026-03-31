# Changelog

All notable changes to this project will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/).

## [0.1.1] - 2026-03-31

### Fixed
- URL scheme validation in docs UI to prevent javascript: XSS

**Full Changelog**: https://github.com/namishsaxena/mcpspec/compare/vTS-0.1.0...vTS-0.1.1

## [0.1.0] - 2026-03-30

### Added
- MCP server introspection via InMemoryTransport with pagination support
- Glob-based include/exclude filtering for tools, resources, and prompts
- Spec generation with YAML and JSON serialization
- JSON Schema validation for mcpspec format
- Self-contained docs UI with dark, light, and high-contrast themes
- Raw HTTP server with `/docs`, `/mcpspec.yaml`, and `/mcp` routes
- `createHandler()` API for composable middleware integration
- Transport and auth metadata in generated specs
- Example Task Manager server with bearer auth and stdio/streamable-http transports

### Security
- XSS prevention in docs HTML rendering
- URL scheme validation for transport endpoints
- Timing-safe bearer token verification in example
- Introspection-only boundary — never calls tools/call, prompts/get, or resources/read
