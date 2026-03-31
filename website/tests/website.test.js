import { readFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, it, expect } from "vitest";
import jsyaml from "js-yaml";

const __dirname = dirname(fileURLToPath(import.meta.url));
const websiteDir = join(__dirname, "..");

describe("website/index.html", () => {
  const html = readFileSync(join(websiteDir, "index.html"), "utf-8");

  it("contains all required page sections", () => {
    expect(html).toContain('class="nav"');
    expect(html).toContain('class="hero"');
    expect(html).toContain('id="code-snippet"');
    expect(html).toContain('class="features"');
    expect(html).toContain('id="viewer"');
    expect(html).toContain('class="trust-headline"');
    expect(html).toContain('class="footer"');
  });

  it("has correct meta tags", () => {
    expect(html).toContain("<title>mcpspec");
    expect(html).toContain('name="description"');
    expect(html).toContain('name="viewport"');
  });

  it("loads IBM Plex fonts from Google Fonts", () => {
    expect(html).toContain("fonts.googleapis.com");
    expect(html).toContain("IBM+Plex+Mono");
    expect(html).toContain("IBM+Plex+Sans");
  });

  it("links to correct external URLs", () => {
    expect(html).toContain("github.com/namishsaxena/mcpspec");
    expect(html).toContain("npmjs.com/package/@mcpspec-dev/typescript");
    expect(html).toContain("pypi.org/project/mcpspec-dev");
    expect(html).toContain("namishsaxena.com");
  });

  it("has shields.io badges", () => {
    expect(html).toContain("img.shields.io/npm/dm/@mcpspec-dev/typescript");
    expect(html).toContain("img.shields.io/pypi/dm/mcpspec-dev");
    expect(html).toContain("img.shields.io/github/stars/namishsaxena/mcpspec");
  });

  it("loads scripts in correct order", () => {
    const jsYamlPos = html.indexOf("js-yaml.min.js");
    const docsTemplatePos = html.indexOf("docs-template.js");
    const exampleSpecPos = html.indexOf("example-spec.js");
    const scriptPos = html.indexOf("script.js");

    expect(jsYamlPos).toBeLessThan(docsTemplatePos);
    expect(docsTemplatePos).toBeLessThan(exampleSpecPos);
    expect(exampleSpecPos).toBeLessThan(scriptPos);
  });

  it("has both TypeScript and Python code panels", () => {
    expect(html).toContain('id="panel-ts"');
    expect(html).toContain('id="panel-py"');
    expect(html).toContain("@mcpspec-dev/typescript");
    expect(html).toContain("mcpspec");
    expect(html).toContain("McpSpec");
  });
});

describe("website/example-spec.js", () => {
  it("contains valid YAML that parses to a complete spec", () => {
    const src = readFileSync(join(websiteDir, "example-spec.js"), "utf-8");
    // Extract the YAML string from the JS file
    const match = src.match(/var EXAMPLE_YAML = `([\s\S]*?)`;/);
    expect(match).not.toBeNull();

    const spec = jsyaml.load(match[1]);
    expect(spec.mcpspec).toBe("0.1.0");
    expect(spec.info.title).toBe("Task Manager");
    expect(spec.tools).toHaveLength(6);
    expect(spec.resources).toHaveLength(1);
    expect(spec.prompts).toHaveLength(1);
  });

  it("includes tools from multiple groups", () => {
    const src = readFileSync(join(websiteDir, "example-spec.js"), "utf-8");
    const match = src.match(/var EXAMPLE_YAML = `([\s\S]*?)`;/);
    const spec = jsyaml.load(match[1]);

    const groups = new Set(spec.tools.map((t) => t.group));
    expect(groups.has("Tasks")).toBe(true);
    expect(groups.has("Analytics")).toBe(true);
  });

  it("includes tools with different annotation types", () => {
    const src = readFileSync(join(websiteDir, "example-spec.js"), "utf-8");
    const match = src.match(/var EXAMPLE_YAML = `([\s\S]*?)`;/);
    const spec = jsyaml.load(match[1]);

    const allAnnotations = spec.tools
      .filter((t) => t.annotations)
      .flatMap((t) => Object.keys(t.annotations));
    expect(allAnnotations).toContain("readOnlyHint");
    expect(allAnnotations).toContain("destructiveHint");
    expect(allAnnotations).toContain("idempotentHint");
  });
});

describe("website/docs-template.js", () => {
  it("exists and contains the docs-ui template", () => {
    const path = join(websiteDir, "docs-template.js");
    expect(existsSync(path)).toBe(true);

    const content = readFileSync(path, "utf-8");
    expect(content).toContain("var DOCS_TEMPLATE");
    expect(content).toContain("__SPEC_DATA__");
    expect(content).toContain("__TITLE__");
  });
});

describe("website/styles.css", () => {
  const css = readFileSync(join(websiteDir, "styles.css"), "utf-8");

  it("uses IBM Plex font families", () => {
    expect(css).toContain("IBM Plex Sans");
    expect(css).toContain("IBM Plex Mono");
  });

  it("uses the correct monochrome palette", () => {
    expect(css).toContain("#09090b");  // --bg-primary
    expect(css).toContain("#fafafa");  // --text-primary
    expect(css).toContain("#111113");  // --bg-elevated
  });

  it("has responsive breakpoint", () => {
    expect(css).toContain("max-width: 640px");
  });
});

describe("website/vercel.json", () => {
  it("is valid JSON with security headers", () => {
    const config = JSON.parse(
      readFileSync(join(websiteDir, "vercel.json"), "utf-8")
    );
    expect(config.headers).toBeDefined();

    const secHeaders = config.headers.find((h) => h.source === "/(.*)");
    expect(secHeaders).toBeDefined();

    const headerNames = secHeaders.headers.map((h) => h.key);
    expect(headerNames).toContain("X-Content-Type-Options");
    expect(headerNames).toContain("X-Frame-Options");
  });
});
