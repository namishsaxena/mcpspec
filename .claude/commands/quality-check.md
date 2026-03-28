Run all quality gates from docs/architecture/quality-gates.md.

```bash
pnpm build && pnpm test
grep -rn ': any' packages/typescript/src/ --include="*.ts" || echo "PASS: No any types"
find packages/typescript/src -name "*.ts" -exec sh -c 'LINES=$(wc -l < "$1"); if [ "$LINES" -gt 300 ]; then echo "FAIL: $1 ($LINES lines)"; fi' _ {} \;
grep -rn "export default" packages/typescript/src/ --include="*.ts" || echo "PASS: No default exports"
grep -rn "^export enum" packages/typescript/src/ --include="*.ts" || echo "PASS: No enums"
```
