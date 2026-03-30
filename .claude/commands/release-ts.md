Release the TypeScript package to npm. Automates pre-flight checks, version bumping, changelog generation, tagging, and pushing.

## Steps

### 1. Pre-flight checks

Verify the working tree is clean and all quality gates pass:

```bash
git diff --quiet && git diff --cached --quiet || echo "FAIL: Uncommitted changes"
pnpm typecheck
pnpm test
pnpm build
```

If any check fails, stop and fix before continuing.

### 2. Determine version bump

Find the last TypeScript release tag and collect commits since then:

```bash
git tag -l "vTS-*" --sort=-v:refname | head -1
```

If no tag exists, this is the first release — use the version already in `packages/typescript/package.json`.

Collect commits since that tag, filtering to TypeScript-scoped changes:
- Commits with `(ts)` or `(docs-ui)` or `(schema)` scope
- Commits touching `packages/typescript/`
- Unscoped commits like `docs:`, `ci:`, `chore:` that are relevant

Determine the bump from commit types:
- Any `fix` → patch
- Any `feat` → minor
- Any `BREAKING CHANGE` or `!` after scope → minor (pre-1.0) or major (post-1.0)
- Highest bump wins

### 3. Generate release notes

Group the commits into sections:

```markdown
## [x.y.z] - YYYY-MM-DD

### Added
- feat commits here

### Fixed
- fix commits here

### Changed
- refactor, perf commits here

### Other
- chore, ci, docs commits here
```

Use commit subjects only (not hashes). Add a "Full Changelog" link at the bottom:
`**Full Changelog**: https://github.com/namishsaxena/mcpspec/compare/vTS-{old}...vTS-{new}`

### 4. Present for review

Show the user:
- Version bump: `0.1.0 → 0.2.0 (minor — N features, N fixes)`
- Draft release notes
- Ask: "Does this look right? Approve to proceed."

Do NOT proceed without explicit approval.

### 5. Apply the release

On approval:

1. Update `version` in `packages/typescript/package.json`
2. Prepend the new release section to `CHANGELOG.md` (above the previous release)
3. Stage and commit:
   ```bash
   git add packages/typescript/package.json CHANGELOG.md
   git commit -m "chore(ts): release x.y.z"
   ```
4. Create tag:
   ```bash
   git tag vTS-x.y.z
   ```

### 6. Push

Ask the user: "Ready to push? This will trigger the npm publish workflow."

On approval:
```bash
git push
git push --tags
```

## Rules

- NEVER skip pre-flight checks
- NEVER proceed without user approval at steps 4 and 6
- NEVER manually edit version — always use this command
- NEVER include Co-Authored-By in the release commit
- Always stage specific files (never `git add -A`)
