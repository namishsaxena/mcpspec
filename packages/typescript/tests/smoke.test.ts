import { describe, it, expect } from "vitest";

describe("smoke test", () => {
  it("confirms vitest is working", () => {
    expect(1 + 1).toBe(2);
  });

  it("confirms ESM imports work", async () => {
    const mod = await import("../src/index.js");
    expect(mod).toBeDefined();
  });
});
