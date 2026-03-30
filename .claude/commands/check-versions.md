Check latest versions of all mcpspec dependencies against npm registry.

Run:

```bash
for pkg in "@modelcontextprotocol/sdk" "js-yaml" "vitest" "typescript" "zod" "@types/node" "@types/js-yaml"; do
  echo "$pkg: $(npm view "$pkg" version 2>/dev/null)"
done
```

Compare with versions in `packages/typescript/package.json` and update if behind.

## Python (PyPI)

```bash
for pkg in "pyyaml" "pydantic" "mcp" "pytest" "pytest-asyncio" "pytest-cov" "mypy" "ruff"; do
  LATEST=$(curl -s "https://pypi.org/pypi/$pkg/json" | python3 -c "import sys,json; print(json.load(sys.stdin)['info']['version'])" 2>/dev/null)
  echo "$pkg: $LATEST"
done
```

Compare with versions in `packages/python/pyproject.toml` and update if behind.
