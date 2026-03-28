# Quality Gates

Every change must pass these gates before merging. These are enforced by CI (when set up) and by manual verification during development.

## Gate 1: Tests Pass

- All unit tests pass: `pnpm test`
- All integration tests pass (when present)
- No skipped tests without a linked issue explaining why
- New code must include tests (TDD preferred)

## Gate 2: Build Succeeds

- `pnpm build` completes with zero errors
- No TypeScript compiler errors in strict mode
- Output files are generated correctly in `dist/`

## Gate 3: Type Safety

- No `any` types in production code (`src/`)
- `any` is permitted in test files only when mocking complex types, and must include a comment explaining why
- All exported functions have explicit return types
- All function parameters are typed

## Gate 4: Lint Clean

- No linting errors or warnings
- No unused imports, variables, or parameters
- Import order follows conventions (node builtins, external, internal)

## Gate 5: File Size Limits

- No production file exceeds 300 lines of code (excluding blank lines and comments)
- No function exceeds 50 lines of code
- Test files are exempt from line limits but should still be organized into focused `describe` blocks

## Gate 6: Dependencies

- All dependencies use latest stable versions (verified against npm/PyPI)
- No known security vulnerabilities (`pnpm audit`)
- MCP SDK is a peer dependency
- No unnecessary dependencies — justify every addition

## Gate 7: Security

- No secrets, API keys, or credentials in code or config
- No `eval()`, `Function()`, or dynamic code execution
- All external input is validated before use
- HTML output is sanitized (XSS prevention)
- See [Security Principles](security-principles.md) for full model

## Gate 8: Manual Verification

At the end of each implementation sub-plan, manually verify:

- The feature works as described in the plan
- Edge cases are handled gracefully
- Error messages are helpful and actionable
- No regressions in existing functionality

## Pre-Commit Checklist

Before every commit, verify:

- [ ] `pnpm test` passes
- [ ] `pnpm build` succeeds
- [ ] No `any` in production code
- [ ] Files under 300 LOC
- [ ] Functions under 50 LOC
- [ ] Commit message follows conventional commits format
- [ ] Only intended files are staged (no `git add -A`)
