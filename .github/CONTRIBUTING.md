# Contributing to mcpspec

Thank you for considering contributing to mcpspec! This guide covers both TypeScript and Python packages.

## Development Setup

### Prerequisites

- **Node.js** >= 22
- **pnpm** >= 9 (`npm install -g pnpm`)
- **Python** >= 3.11 (for Python package, Phase 2)
- **uv** (for Python package management, Phase 2)

### Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/<your-username>/mcpspec.git
   cd mcpspec
   ```
3. Install dependencies:
   ```bash
   pnpm install
   ```
4. Build all packages:
   ```bash
   pnpm build
   ```
5. Run tests:
   ```bash
   pnpm test
   ```

## Development Workflow

### Branch Naming

- `feat/<name>` — new features
- `fix/<name>` — bug fixes
- `chore/<name>` — maintenance tasks
- `docs/<name>` — documentation changes

### Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description
```

- **Types:** `feat`, `fix`, `chore`, `docs`, `test`, `refactor`, `ci`, `style`, `perf`
- **Scopes:** `ts`, `py`, `schema`, `docs-ui`, `example`, `ci`
- Keep subject under 72 characters
- Use imperative mood: "add feature" not "added feature"

### Code Standards

All code must follow the standards documented in `docs/architecture/`:

- `coding-standards.md` — language-specific rules
- `quality-gates.md` — checks that must pass before merge
- `security-principles.md` — security constraints
- `modularity-guidelines.md` — file/function size limits

**Key rules:**
- No file exceeds 300 lines of code (excluding tests)
- No function exceeds 50 lines
- No `any` type in TypeScript production code
- All tests must pass
- Build must succeed with zero errors

### Testing

- Write tests for all new code
- Use TDD where practical: failing test first, then implement
- Test files: `<module>.test.ts` (TypeScript), `test_<module>.py` (Python)
- Tests live in the `tests/` directory of each package

### Pull Requests

1. Create a feature branch from `main`
2. Make your changes following the code standards
3. Write/update tests
4. Ensure all quality gates pass:
   ```bash
   pnpm build && pnpm test
   ```
5. Push your branch and open a PR
6. Fill in the PR template completely
7. Wait for review

### Review Process

- All PRs require at least one review
- Address all review comments
- Ensure CI passes before requesting re-review
- Squash and merge when approved

### Docs UI

The interactive documentation page is built from source files in `docs-ui/`:

- `docs-ui/index.html` — HTML template with `__STYLES__` and `__SCRIPT__` placeholders
- `docs-ui/styles.css` — all styles
- `docs-ui/script.js` — client-side logic

The build script `scripts/build-docs-ui.js` bundles these into a single self-contained HTML file. This runs automatically as part of `pnpm build` — no manual step needed. The bundled output (`packages/typescript/src/ui/docs.html`) is gitignored and regenerated on every build.

## Project Structure

```
mcpspec/
├── packages/typescript/    # npm: @mcpspec-dev/typescript
├── packages/python/        # PyPI: mcpspec-dev (coming soon)
├── schema/                 # JSON Schema for mcpspec.yaml
├── docs-ui/                # Docs HTML/CSS/JS source (bundled into package)
├── scripts/                # Build scripts (docs-ui bundler)
├── examples/               # Example MCP servers
├── docs/                   # Guides and architecture docs
└── website/                # mcpspec.dev (coming soon)
```

## Questions?

Open a [Discussion](https://github.com/namishsaxena/mcpspec/discussions) or file an [Issue](https://github.com/namishsaxena/mcpspec/issues).
