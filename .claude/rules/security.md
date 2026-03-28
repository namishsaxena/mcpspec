---
description: Security rules for mcpspec source code
globs:
  - "packages/typescript/src/**"
  - "packages/python/src/**"
---

# Security Rules

These rules apply to all source code in the mcpspec packages.

## Input Validation

- Validate all inputs at system boundaries: MCP protocol responses, user-provided options.
- Do not trust MCP server responses — they are external input. Validate structure before accessing nested fields.
- Validate types and ranges: if a function expects a number, verify it is a number.

## HTML Sanitization

- Sanitize ALL MCP-sourced strings before rendering in HTML output.
- Escape these characters: `<` → `&lt;`, `>` → `&gt;`, `&` → `&amp;`, `"` → `&quot;`, `'` → `&#x27;`
- This applies to: tool names, tool descriptions, resource names, resource URIs, prompt names, prompt descriptions.

## No Dynamic Code Execution

- Never use `eval()`.
- Never use `new Function()`.
- Never use dynamic `import()` with user-controlled paths.
- Never construct code strings for execution.

## No Secret Exposure

- Never log secrets, tokens, or API keys.
- Never include internal URLs in error messages shown to users.
- Never include stack traces in user-facing output.

## URL Validation

- Any URL rendered as a clickable link must start with `http://` or `https://`.
- Reject `javascript:`, `data:`, `vbscript:`, and protocol-relative (`//`) URLs.

## Constant-Time Comparison

- Use constant-time comparison for any security-sensitive string matching (e.g., comparing tokens, hashes).
- In Node.js: `crypto.timingSafeEqual()`.
