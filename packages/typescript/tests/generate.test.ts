import { describe, it, expect } from "vitest";
import yaml from "js-yaml";
import { generateSpec, serializeSpec } from "../src/generate.js";
import type { IntrospectionResult } from "../src/introspect.js";
import type { McpSpecOptions, McpSpec } from "../src/types.js";

function createTestIntrospection(): IntrospectionResult {
  return {
    tools: [
      {
        name: "get_users",
        description: "Retrieve a list of users",
        inputSchema: {
          type: "object",
          properties: {
            limit: { type: "number", description: "Max users to return" },
            offset: { type: "number", description: "Pagination offset" },
          },
        },
      },
      {
        name: "create_user",
        description: "Create a new user account",
        annotations: {
          readOnlyHint: false,
          destructiveHint: false,
        },
        inputSchema: {
          type: "object",
          properties: {
            name: { type: "string", description: "User full name" },
            email: { type: "string", description: "User email" },
          },
          required: ["name", "email"],
        },
      },
      {
        name: "delete_user",
        description: "Delete a user permanently",
        annotations: {
          readOnlyHint: false,
          destructiveHint: true,
        },
        inputSchema: {
          type: "object",
          properties: {
            id: { type: "string", description: "User ID to delete" },
          },
          required: ["id"],
        },
      },
      {
        name: "internal_debug",
        description: "Internal debugging tool",
        inputSchema: { type: "object", properties: {} },
      },
    ],
    resources: [
      {
        uri: "users://list",
        name: "users-list",
        description: "List of all users",
        mimeType: "application/json",
      },
    ],
    prompts: [
      {
        name: "user_report",
        description: "Generate a user activity report",
        arguments: [
          {
            name: "timeframe",
            description: "Report timeframe",
            required: true,
          },
          {
            name: "format",
            description: "Output format",
            required: false,
          },
        ],
      },
    ],
    capabilities: {
      tools: { listChanged: true },
      resources: { subscribe: false },
    },
  };
}

function createTestOptions(): McpSpecOptions {
  return {
    info: {
      title: "User Management Server",
      description: "Manages users and their accounts",
      version: "1.0.0",
      repository: "https://github.com/example/user-server",
      license: "MIT",
    },
  };
}

describe("generateSpec", () => {
  it("generates a spec from tools, resources, and prompts", () => {
    const introspection = createTestIntrospection();
    const options = createTestOptions();

    const spec = generateSpec(introspection, options);

    expect(spec.mcpspec).toBe("0.1.0");
    expect(spec.info.name).toBe("user-management-server");
    expect(spec.info.title).toBe("User Management Server");
    expect(spec.info.version).toBe("1.0.0");
    expect(spec.info.description).toBe(
      "Manages users and their accounts",
    );
    expect(spec.info.repository).toBe(
      "https://github.com/example/user-server",
    );
    expect(spec.info.license).toBe("MIT");

    expect(spec.tools).toHaveLength(4);
    expect(spec.resources).toHaveLength(1);
    expect(spec.prompts).toHaveLength(1);
    expect(spec.capabilities).toBeDefined();
  });

  it("maps tool fields correctly", () => {
    const introspection = createTestIntrospection();
    const options = createTestOptions();

    const spec = generateSpec(introspection, options);

    const createUser = spec.tools?.find(
      (t) => t.name === "create_user",
    );
    expect(createUser).toBeDefined();
    expect(createUser?.description).toBe("Create a new user account");
    expect(createUser?.inputSchema).toBeDefined();
    expect(createUser?.annotations?.readOnlyHint).toBe(false);
    expect(createUser?.annotations?.destructiveHint).toBe(false);
  });

  it("maps resource fields correctly", () => {
    const introspection = createTestIntrospection();
    const options = createTestOptions();

    const spec = generateSpec(introspection, options);

    const resource = spec.resources?.[0];
    expect(resource).toBeDefined();
    expect(resource?.uri).toBe("users://list");
    expect(resource?.name).toBe("users-list");
    expect(resource?.description).toBe("List of all users");
    expect(resource?.mimeType).toBe("application/json");
  });

  it("maps prompt fields correctly", () => {
    const introspection = createTestIntrospection();
    const options = createTestOptions();

    const spec = generateSpec(introspection, options);

    const prompt = spec.prompts?.[0];
    expect(prompt).toBeDefined();
    expect(prompt?.name).toBe("user_report");
    expect(prompt?.description).toBe(
      "Generate a user activity report",
    );
    expect(prompt?.arguments).toHaveLength(2);
    expect(prompt?.arguments?.[0]?.name).toBe("timeframe");
    expect(prompt?.arguments?.[0]?.required).toBe(true);
    expect(prompt?.arguments?.[1]?.name).toBe("format");
    expect(prompt?.arguments?.[1]?.required).toBe(false);
  });

  it("includes transport when provided in options", () => {
    const introspection = createTestIntrospection();
    const options: McpSpecOptions = {
      ...createTestOptions(),
      transport: [
        {
          type: "streamable-http",
          url: "https://example.com/mcp",
          description: "Primary HTTP endpoint",
          auth: {
            type: "bearer",
            description: "Use a valid API token",
          },
        },
      ],
    };

    const spec = generateSpec(introspection, options);

    expect(spec.transport).toHaveLength(1);
    expect(spec.transport?.[0]?.type).toBe("streamable-http");
    expect(spec.transport?.[0]?.url).toBe("https://example.com/mcp");
    expect(spec.transport?.[0]?.description).toBe("Primary HTTP endpoint");
    expect(spec.transport?.[0]?.auth?.type).toBe("bearer");
    expect(spec.transport?.[0]?.auth?.description).toBe("Use a valid API token");
  });

  it("includes $schema URL", () => {
    const introspection = createTestIntrospection();
    const options = createTestOptions();

    const spec = generateSpec(introspection, options);

    expect(spec.$schema).toBe(
      "https://mcpspec.dev/schema/0.1.0.json",
    );
  });
});

describe("generateSpec — filtering", () => {
  it("excludes tools matching exclude patterns", () => {
    const introspection = createTestIntrospection();
    const options: McpSpecOptions = {
      ...createTestOptions(),
      exclude: ["internal_*"],
    };

    const spec = generateSpec(introspection, options);

    expect(spec.tools).toHaveLength(3);
    expect(
      spec.tools?.find((t) => t.name === "internal_debug"),
    ).toBeUndefined();
    expect(
      spec.tools?.find((t) => t.name === "get_users"),
    ).toBeDefined();
  });

  it("includes only tools matching include patterns", () => {
    const introspection = createTestIntrospection();
    const options: McpSpecOptions = {
      ...createTestOptions(),
      include: ["get_*", "create_*"],
    };

    const spec = generateSpec(introspection, options);

    expect(spec.tools).toHaveLength(2);
    expect(
      spec.tools?.find((t) => t.name === "get_users"),
    ).toBeDefined();
    expect(
      spec.tools?.find((t) => t.name === "create_user"),
    ).toBeDefined();
  });

  it("applies filtering to resources", () => {
    const introspection = createTestIntrospection();
    const options: McpSpecOptions = {
      ...createTestOptions(),
      exclude: ["users-list"],
    };

    const spec = generateSpec(introspection, options);

    expect(spec.resources).toHaveLength(0);
  });

  it("applies filtering to prompts", () => {
    const introspection = createTestIntrospection();
    const options: McpSpecOptions = {
      ...createTestOptions(),
      exclude: ["user_*"],
    };

    const spec = generateSpec(introspection, options);

    // user_report is excluded, but tools like get_users are also
    // excluded because they match user_* — wait, get_users does NOT
    // match user_* (it's get_users, not user_get). Let's verify:
    expect(spec.prompts).toHaveLength(0);
    // get_users does not match user_*, so it survives
    expect(
      spec.tools?.find((t) => t.name === "get_users"),
    ).toBeDefined();
  });
});

describe("generateSpec — overrides", () => {
  it("applies tool overrides for description", () => {
    const introspection = createTestIntrospection();
    const options: McpSpecOptions = {
      ...createTestOptions(),
      overrides: {
        tools: {
          get_users: {
            description: "Fetches user list from the database",
          },
        },
      },
    };

    const spec = generateSpec(introspection, options);

    const getUsers = spec.tools?.find((t) => t.name === "get_users");
    expect(getUsers?.description).toBe(
      "Fetches user list from the database",
    );
  });

  it("applies tool overrides for title", () => {
    const introspection = createTestIntrospection();
    const options: McpSpecOptions = {
      ...createTestOptions(),
      overrides: {
        tools: {
          create_user: {
            title: "Create User Account",
          },
        },
      },
    };

    const spec = generateSpec(introspection, options);

    const createUser = spec.tools?.find(
      (t) => t.name === "create_user",
    );
    expect(createUser?.title).toBe("Create User Account");
  });

  it("applies tool overrides for group", () => {
    const introspection = createTestIntrospection();
    const options: McpSpecOptions = {
      ...createTestOptions(),
      overrides: {
        tools: {
          get_users: { group: "Users" },
          create_user: { group: "Users" },
        },
      },
    };

    const spec = generateSpec(introspection, options);

    const getUsers = spec.tools?.find((t) => t.name === "get_users");
    const createUser = spec.tools?.find(
      (t) => t.name === "create_user",
    );
    expect(getUsers?.group).toBe("Users");
    expect(createUser?.group).toBe("Users");
  });

  it("applies resource overrides for description", () => {
    const introspection = createTestIntrospection();
    const options: McpSpecOptions = {
      ...createTestOptions(),
      overrides: {
        resources: {
          "users-list": {
            description: "All registered users as JSON",
          },
        },
      },
    };

    const spec = generateSpec(introspection, options);

    const resource = spec.resources?.[0];
    expect(resource?.description).toBe(
      "All registered users as JSON",
    );
  });

  it("applies prompt overrides for description", () => {
    const introspection = createTestIntrospection();
    const options: McpSpecOptions = {
      ...createTestOptions(),
      overrides: {
        prompts: {
          user_report: {
            description: "Custom report description",
          },
        },
      },
    };

    const spec = generateSpec(introspection, options);

    const prompt = spec.prompts?.[0];
    expect(prompt?.description).toBe("Custom report description");
  });
});

describe("generateSpec — groups", () => {
  it("assigns groups to tools via groups option", () => {
    const introspection = createTestIntrospection();
    const options: McpSpecOptions = {
      ...createTestOptions(),
      groups: {
        "User Management": ["get_users", "create_user", "delete_user"],
        "Internal": ["internal_debug"],
      },
    };

    const spec = generateSpec(introspection, options);

    const getUsers = spec.tools?.find((t) => t.name === "get_users");
    const createUser = spec.tools?.find(
      (t) => t.name === "create_user",
    );
    const debug = spec.tools?.find(
      (t) => t.name === "internal_debug",
    );
    expect(getUsers?.group).toBe("User Management");
    expect(createUser?.group).toBe("User Management");
    expect(debug?.group).toBe("Internal");
  });

  it("override group takes precedence over groups option", () => {
    const introspection = createTestIntrospection();
    const options: McpSpecOptions = {
      ...createTestOptions(),
      groups: {
        "User Management": ["get_users"],
      },
      overrides: {
        tools: {
          get_users: { group: "Custom Group" },
        },
      },
    };

    const spec = generateSpec(introspection, options);

    const getUsers = spec.tools?.find((t) => t.name === "get_users");
    expect(getUsers?.group).toBe("Custom Group");
  });
});

describe("generateSpec — examples", () => {
  it("attaches examples to tools via examples option", () => {
    const introspection = createTestIntrospection();
    const options: McpSpecOptions = {
      ...createTestOptions(),
      examples: {
        get_users: [
          {
            title: "Get first 10 users",
            input: { limit: 10 },
            description: "Returns the first 10 users",
          },
          {
            title: "Get users with offset",
            input: { limit: 5, offset: 20 },
          },
        ],
      },
    };

    const spec = generateSpec(introspection, options);

    const getUsers = spec.tools?.find((t) => t.name === "get_users");
    expect(getUsers?.examples).toHaveLength(2);
    expect(getUsers?.examples?.[0]?.title).toBe("Get first 10 users");
    expect(getUsers?.examples?.[0]?.input).toEqual({ limit: 10 });
    expect(getUsers?.examples?.[0]?.description).toBe(
      "Returns the first 10 users",
    );
    expect(getUsers?.examples?.[1]?.title).toBe(
      "Get users with offset",
    );
    expect(getUsers?.examples?.[1]?.input).toEqual({
      limit: 5,
      offset: 20,
    });
  });

  it("tools without examples have no examples field", () => {
    const introspection = createTestIntrospection();
    const options: McpSpecOptions = {
      ...createTestOptions(),
      examples: {
        get_users: [
          { title: "Example", input: { limit: 5 } },
        ],
      },
    };

    const spec = generateSpec(introspection, options);

    const createUser = spec.tools?.find(
      (t) => t.name === "create_user",
    );
    expect(createUser?.examples).toBeUndefined();
  });
});

describe("serializeSpec", () => {
  it("serializes spec to valid YAML that round-trips", () => {
    const introspection = createTestIntrospection();
    const options = createTestOptions();
    const spec = generateSpec(introspection, options);

    const yamlStr = serializeSpec(spec);

    expect(typeof yamlStr).toBe("string");
    expect(yamlStr.length).toBeGreaterThan(0);

    // Round-trip: YAML string -> parse -> should match original spec
    const parsed = yaml.load(yamlStr) as McpSpec;
    expect(parsed.mcpspec).toBe("0.1.0");
    expect(parsed.info.name).toBe("user-management-server");
    expect(parsed.info.title).toBe("User Management Server");
    expect(parsed.tools).toHaveLength(4);
    expect(parsed.resources).toHaveLength(1);
    expect(parsed.prompts).toHaveLength(1);
  });

  it("produces YAML with expected top-level keys", () => {
    const introspection = createTestIntrospection();
    const options = createTestOptions();
    const spec = generateSpec(introspection, options);

    const yamlStr = serializeSpec(spec);

    expect(yamlStr).toContain("mcpspec:");
    expect(yamlStr).toContain("info:");
    expect(yamlStr).toContain("tools:");
    expect(yamlStr).toContain("resources:");
    expect(yamlStr).toContain("prompts:");
    expect(yamlStr).toContain("capabilities:");
  });

  it("omits transport when not present in spec", () => {
    const introspection = createTestIntrospection();
    const options = createTestOptions();
    const spec = generateSpec(introspection, options);

    const yamlStr = serializeSpec(spec);

    expect(yamlStr).not.toContain("transport:");
  });

  it("includes transport when present in spec", () => {
    const introspection = createTestIntrospection();
    const options: McpSpecOptions = {
      ...createTestOptions(),
      transport: [
        {
          type: "streamable-http",
          url: "https://example.com/mcp",
          description: "Main endpoint",
          auth: {
            type: "bearer",
            description: "Requires API token",
          },
        },
      ],
    };
    const spec = generateSpec(introspection, options);

    const yamlStr = serializeSpec(spec);

    expect(yamlStr).toContain("transport:");
    expect(yamlStr).toContain("streamable-http");
    expect(yamlStr).toContain("Main endpoint");
    expect(yamlStr).toContain("Requires API token");
  });
});
