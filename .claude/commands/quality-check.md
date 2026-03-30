Run all quality gates from docs/architecture/quality-gates.md.

## TypeScript

```bash
pnpm build && pnpm test
grep -rn ': any' packages/typescript/src/ --include="*.ts" || echo "PASS: No any types"
find packages/typescript/src -name "*.ts" -exec sh -c 'LINES=$(wc -l < "$1"); if [ "$LINES" -gt 300 ]; then echo "FAIL: $1 ($LINES lines)"; fi' _ {} \;
grep -rn "export default" packages/typescript/src/ --include="*.ts" || echo "PASS: No default exports"
grep -rn "^export enum" packages/typescript/src/ --include="*.ts" || echo "PASS: No enums"
```

## Python

```bash
cd packages/python
uv run pytest --tb=short
uv run pytest --cov --cov-fail-under=90 --cov-report=term-missing
uv run mypy --strict src/
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
find src -name "*.py" -exec sh -c 'LINES=$(wc -l < "$1"); if [ "$LINES" -gt 300 ]; then echo "FAIL: $1 ($LINES lines)"; fi' _ {} \;
```
