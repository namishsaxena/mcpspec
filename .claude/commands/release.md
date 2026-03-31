Smart umbrella release command. Detects which packages have changes and releases them.

## Steps

### 1. Pre-flight — ALL quality gates pass (both languages)

```bash
# TypeScript
pnpm typecheck && pnpm test && pnpm build

# Python
cd packages/python && uv run pytest && uv run mypy --strict src/ && uv run ruff check && cd ../..
```

If any check fails, stop and fix before continuing.

### 2. Detect changes since last tags

```bash
# Last TypeScript tag
TS_TAG=$(git tag -l "vTS-*" --sort=-v:refname | head -1)
echo "Last TS tag: $TS_TAG"

# Commits since last TS tag touching TS-relevant paths
git log ${TS_TAG}..HEAD --oneline -- packages/typescript/ docs-ui/ schema/ | head -20

# Last Python tag
PY_TAG=$(git tag -l "vPY-*" --sort=-v:refname | head -1)
echo "Last PY tag: $PY_TAG"

# Commits since last PY tag touching Python-relevant paths
git log ${PY_TAG}..HEAD --oneline -- packages/python/ docs-ui/ schema/ | head -20
```

Shared changes (`docs-ui/`, `schema/`) trigger both packages.

### 3. Determine semver bump for each affected package

From commit types (feat -> minor, fix -> patch, BREAKING CHANGE -> major/minor).

### 4. Present plan

Format: "TS: 0.1.0 -> 0.2.0 (2 features, 1 fix), PY: 0.1.0 -> 0.1.1 (1 fix)" or "PY: skip (no changes)"

### 5. Hygiene checks

Before user approval, verify:
- [ ] Package-specific CHANGELOG.md has entry for new version(s)
- [ ] README install commands reference correct versions
- [ ] Example servers build and run
- [ ] `docs-ui/` build is fresh
- [ ] All cross-language tests pass

### 6. User approves — explicit confirmation required

Do NOT proceed without explicit approval.

### 7. Execute for each package that needs release

Run `/release-ts` and/or `/release-py` as appropriate.

## Rules

- NEVER proceed without explicit user approval
- NEVER release if quality gates fail
- NEVER include Co-Authored-By in the release commit
- Shared changes (docs-ui, schema) trigger BOTH packages
- Each package gets its own tag (`vTS-x.y.z` / `vPY-x.y.z`)
- Always stage specific files (never `git add -A`)
