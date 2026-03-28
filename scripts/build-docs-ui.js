import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");

const html = readFileSync(join(root, "docs-ui/index.html"), "utf-8");
const css = readFileSync(join(root, "docs-ui/styles.css"), "utf-8");
const js = readFileSync(join(root, "docs-ui/script.js"), "utf-8");

const output = html
  .replace("__STYLES__", css)
  .replace("__SCRIPT__", js);

const tsUiDir = join(root, "packages/typescript/src/ui");
mkdirSync(tsUiDir, { recursive: true });
writeFileSync(join(tsUiDir, "docs.html"), output, "utf-8");

console.log("Built docs UI -> packages/typescript/src/ui/docs.html");
console.log("  Size: " + Buffer.byteLength(output, "utf-8") + " bytes");
