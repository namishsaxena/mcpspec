Check latest versions of all mcpspec dependencies against npm registry.

Run:

```bash
for pkg in "@modelcontextprotocol/sdk" "js-yaml" "vitest" "typescript" "zod" "@types/node" "@types/js-yaml"; do
  echo "$pkg: $(npm view "$pkg" version 2>/dev/null)"
done
```

Compare with versions in `packages/typescript/package.json` and update if behind.
