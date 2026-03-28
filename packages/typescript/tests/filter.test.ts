import { describe, it, expect } from "vitest";
import { filterItems } from "../src/filter.js";
import type { FilterOptions } from "../src/filter.js";

interface NamedItem {
  name: string;
  description?: string;
}

const testItems: NamedItem[] = [
  { name: "get_users", description: "Get users" },
  { name: "create_user", description: "Create a user" },
  { name: "delete_user", description: "Delete a user" },
  { name: "internal_debug", description: "Debug tool" },
  { name: "internal_metrics", description: "Metrics tool" },
  { name: "admin_reset", description: "Reset everything" },
  { name: "public_status", description: "Public status" },
];

describe("filterItems", () => {
  it("returns all items when no filters are set", () => {
    const result = filterItems(testItems, {});
    expect(result).toHaveLength(7);
    expect(result).toEqual(testItems);
  });

  it("excludes items matching glob patterns", () => {
    const options: FilterOptions = {
      exclude: ["internal_*"],
    };
    const result = filterItems(testItems, options);

    expect(result).toHaveLength(5);
    expect(result.find((i) => i.name === "internal_debug")).toBeUndefined();
    expect(result.find((i) => i.name === "internal_metrics")).toBeUndefined();
    expect(result.find((i) => i.name === "get_users")).toBeDefined();
  });

  it("excludes items matching multiple glob patterns", () => {
    const options: FilterOptions = {
      exclude: ["internal_*", "admin_*"],
    };
    const result = filterItems(testItems, options);

    expect(result).toHaveLength(4);
    expect(result.find((i) => i.name === "internal_debug")).toBeUndefined();
    expect(result.find((i) => i.name === "admin_reset")).toBeUndefined();
    expect(result.find((i) => i.name === "get_users")).toBeDefined();
  });

  it("includes only items matching glob patterns", () => {
    const options: FilterOptions = {
      include: ["get_*", "public_*"],
    };
    const result = filterItems(testItems, options);

    expect(result).toHaveLength(2);
    expect(result.find((i) => i.name === "get_users")).toBeDefined();
    expect(result.find((i) => i.name === "public_status")).toBeDefined();
  });

  it("include takes precedence over exclude when both are set", () => {
    const options: FilterOptions = {
      include: ["get_*", "create_*"],
      exclude: ["get_*"],
    };
    const result = filterItems(testItems, options);

    // include wins — only get_* and create_* are included
    expect(result).toHaveLength(2);
    expect(result.find((i) => i.name === "get_users")).toBeDefined();
    expect(result.find((i) => i.name === "create_user")).toBeDefined();
  });

  it("handles exact name matches in exclude", () => {
    const options: FilterOptions = {
      exclude: ["delete_user", "admin_reset"],
    };
    const result = filterItems(testItems, options);

    expect(result).toHaveLength(5);
    expect(result.find((i) => i.name === "delete_user")).toBeUndefined();
    expect(result.find((i) => i.name === "admin_reset")).toBeUndefined();
  });

  it("handles wildcard-only pattern", () => {
    const options: FilterOptions = {
      include: ["*_user"],
    };
    const result = filterItems(testItems, options);

    // *_user matches create_user and delete_user but not get_users (ends with 's')
    expect(result).toHaveLength(2);
    expect(result.find((i) => i.name === "get_users")).toBeUndefined();
    expect(result.find((i) => i.name === "create_user")).toBeDefined();
    expect(result.find((i) => i.name === "delete_user")).toBeDefined();
  });

  it("handles empty include array (returns nothing)", () => {
    const options: FilterOptions = {
      include: [],
    };
    const result = filterItems(testItems, options);

    // empty include = explicit allowlist with nothing allowed
    expect(result).toHaveLength(0);
  });

  it("handles empty exclude array (returns everything)", () => {
    const options: FilterOptions = {
      exclude: [],
    };
    const result = filterItems(testItems, options);

    expect(result).toHaveLength(7);
  });
});
