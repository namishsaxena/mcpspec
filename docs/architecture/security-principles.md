# Security Principles

## Core Principle

**The spec is a publication, not a dump.** mcpspec exists to document MCP servers. It is a read-only introspection tool. It never executes, mutates, or accesses actual data.

## Threat Model

### What mcpspec protects against

1. **Accidental exposure of internal tools.** Authors can exclude tools from the spec using `exclude` patterns or `include` allowlists.
2. **XSS in the docs page.** All tool names, descriptions, and schema values are sanitized before rendering in HTML.
3. **Secrets in generated specs.** mcpspec never includes environment variables, auth tokens, or internal configuration in the output.

### What mcpspec does NOT protect against

1. **Malicious MCP server authors.** If the server intentionally serves misleading specs, mcpspec cannot detect that. The spec reflects what the server reports.
2. **Network-level attacks.** Transport security (TLS, auth) is the server's responsibility, not mcpspec's.
3. **Denial of service.** Rate limiting the docs endpoint is the server operator's responsibility.

## Hard Rules

### Never call execution endpoints

mcpspec MUST only use these MCP methods:

| Allowed | Forbidden |
|---------|-----------|
| `tools/list` | `tools/call` |
| `resources/list` | `resources/read` |
| `resources/listTemplates` | `resources/subscribe` |
| `prompts/list` | `prompts/get` |
| `initialize` | Any other RPC |

**Rationale:** Calling `tools/call` could trigger side effects. Calling `resources/read` could access sensitive data. Calling `prompts/get` could expose proprietary prompt content. mcpspec has no business doing any of this.

### Never trust external input

- All MCP protocol responses must be validated before use (schema validation with Zod)
- Tool descriptions, names, and parameter schemas may contain arbitrary strings — always sanitize before HTML rendering
- Never interpolate raw strings into HTML without escaping
- Never use `eval()`, `new Function()`, or any dynamic code execution

### Never include secrets

- No environment variables in generated specs
- No auth tokens, API keys, or passwords
- No internal URLs or infrastructure details unless the author explicitly provides them in config
- The `transport.auth` block documents auth requirements (what type of auth), never actual credentials

### Sanitization Requirements

Before rendering any MCP-sourced string in HTML:

1. Escape HTML entities: `<`, `>`, `&`, `"`, `'`
2. Strip or escape any HTML tags in descriptions
3. Validate URLs before rendering as links (must be `http://` or `https://`)
4. Limit string lengths to prevent layout-breaking content (max 10,000 characters per field)

### Dependency Security

- Run `pnpm audit` before releases
- Keep dependencies minimal — every dependency is an attack surface
- Prefer well-maintained packages with active security response teams
- Review changelogs before major version upgrades

## Security Checklist for New Features

When adding any new feature, answer these questions:

- [ ] Does this feature access any MCP endpoint beyond `list`? If yes, **STOP**.
- [ ] Does this feature render user-controlled strings in HTML? If yes, sanitize.
- [ ] Does this feature include any environment or runtime data in output? If yes, review what's included.
- [ ] Does this feature add a new dependency? If yes, audit it.
- [ ] Could this feature be used to enumerate internal server details that the author didn't intend to expose? If yes, add controls.
