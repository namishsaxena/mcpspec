# mcpspec

OpenAPI-like specs for MCP servers. Introspects tools/resources/prompts via MCP protocol, generates `mcpspec.yaml`, serves `/docs` and `/mcpspec.yaml`.

## Non-Negotiable Rules

- NEVER include Co-Authored-By, Signed-off-by, or any AI attribution in commits
- NEVER use `git add -A` or `git add .` — always stage specific files
- NEVER commit .env, credentials, secrets, or API keys
- NEVER use `any` in TypeScript production code — use `unknown` and narrow
- NEVER call tools/call, prompts/get, or resources/read — only list endpoints

## Commands

- Build: `pnpm build`
- Test: `pnpm test`
- Typecheck: `pnpm typecheck`
- Single test: `cd packages/typescript && pnpm vitest run tests/<file>.test.ts`
- Python test: `cd packages/python && uv run pytest`
- Python typecheck: `cd packages/python && uv run mypy --strict src/`
- Python lint: `cd packages/python && uv run ruff check`
- Python single test: `cd packages/python && uv run pytest tests/test_<file>.py`

## Commit Conventions

Conventional commits: `type(scope): description`
- Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`, `perf`
- Scopes: `ts`, `py`, `schema`, `docs-ui`, `example`, `ci`
- Imperative mood, 72 char subject max

## Release Process

- Use `/release-ts` command to release TypeScript package
- Use `/release-py` command to release Python packages
- Version is auto-determined from conventional commits since last tag
- Tag format: `vTS-x.y.z` (TypeScript), `vPY-x.y.z` (Python)
- Package name: `@mcpspec-dev/typescript` on npm
- Package: `mcpspec-dev` on PyPI
- Never manually edit version in package.json — the release command handles it

## Code Limits

- **300 LOC max** per file (excluding tests)
- **50 LOC max** per function
- Refactor into smaller modules when approaching limits

## Dependencies

- Always verify latest version from npm/PyPI before adding — NEVER guess
- MCP SDK is a peer dependency
- Pin with caret: `^x.y.z`

## Key Decisions

| Decision | Resolution |
|----------|-----------|
| HTTP framework | Raw Node.js `http` — only 3 routes, zero framework dep on users |
| Introspection | In-memory MCP client via InMemoryTransport |
| Package managers | pnpm (TypeScript), uv (Python) |
| Testing | vitest with TDD |
| Security | Only list endpoints, never get/read/call |

## Architecture

Detailed standards in `docs/architecture/`:
- [Coding Standards](docs/architecture/coding-standards.md)
- [Quality Gates](docs/architecture/quality-gates.md)
- [Security Principles](docs/architecture/security-principles.md)
- [Modularity Guidelines](docs/architecture/modularity-guidelines.md)
