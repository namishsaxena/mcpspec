// Pre-loaded example spec for the viewer — Task Manager MCP server
var EXAMPLE_YAML = `mcpspec: "0.1.0"
$schema: "https://mcpspec.dev/schema/0.1.0.json"

info:
  name: task-manager
  version: "1.0.0"
  title: Task Manager
  description: |
    A task management MCP server for demonstration.
    Supports creating, reading, updating, and deleting tasks
    with status tracking and priority levels.
  repository: https://github.com/namishsaxena/mcpspec
  license: MIT
  authors:
    - name: Namish Saxena
      url: https://mcpspec.dev

transport:
  - type: streamable-http
    url: /mcp
    description: Primary HTTP endpoint for browser and remote clients
    auth:
      type: bearer
      description: Set API_TOKEN env var or use the default demo token
  - type: stdio
    command: npx mcpspec-example-task-manager
    description: Local stdio transport for CLI and desktop clients

capabilities:
  tools:
    listChanged: true
  resources: {}
  prompts: {}

tools:
  - name: create_task
    description: Create a new task with a title, optional description, and priority
    group: Tasks
    annotations:
      idempotentHint: false
      openWorldHint: false
    inputSchema:
      type: object
      properties:
        title:
          type: string
          description: Task title
        description:
          type: string
          description: Detailed task description
        priority:
          type: string
          description: Task priority level (defaults to medium)
          enum:
            - low
            - medium
            - high
      required:
        - title
    examples:
      - title: Create a simple task
        input:
          title: Buy groceries
          description: Milk, eggs, bread
        description: Creates a new task with default medium priority
      - title: Create a high-priority task
        input:
          title: Fix production bug
          description: Users seeing 500 errors on /api/checkout
          priority: high
        description: Creates an urgent task with high priority

  - name: get_task
    description: Retrieve a single task by its ID
    group: Tasks
    annotations:
      readOnlyHint: true
      idempotentHint: true
      openWorldHint: false
    inputSchema:
      type: object
      properties:
        id:
          type: string
          description: Task ID
      required:
        - id
    examples:
      - title: Fetch task by ID
        input:
          id: "1"
        description: Retrieves the full task object for task #1

  - name: list_tasks
    description: List tasks with optional filtering by status and priority
    group: Tasks
    annotations:
      readOnlyHint: true
      idempotentHint: true
      openWorldHint: false
    inputSchema:
      type: object
      properties:
        status:
          type: string
          description: Filter by task status
          enum:
            - todo
            - in_progress
            - done
        priority:
          type: string
          description: Filter by priority level
          enum:
            - low
            - medium
            - high
        limit:
          type: integer
          description: Maximum number of tasks to return (default 25, max 100)
          maximum: 100
          minimum: 1
      required: []
    examples:
      - title: List in-progress tasks
        input:
          status: in_progress
          limit: 10
        description: Returns up to 10 tasks that are currently in progress
      - title: List high-priority todos
        input:
          status: todo
          priority: high
        description: Find all high-priority tasks that haven't been started

  - name: update_task
    description: Update fields on an existing task
    group: Tasks
    annotations:
      idempotentHint: true
      openWorldHint: false
    inputSchema:
      type: object
      properties:
        id:
          type: string
          description: Task ID
        title:
          type: string
          description: New title
        description:
          type: string
          description: New description
        status:
          type: string
          description: New status
          enum:
            - todo
            - in_progress
            - done
        priority:
          type: string
          description: New priority
          enum:
            - low
            - medium
            - high
      required:
        - id

  - name: delete_task
    description: Permanently delete a task by ID
    group: Tasks
    annotations:
      destructiveHint: true
      idempotentHint: true
      openWorldHint: false
    inputSchema:
      type: object
      properties:
        id:
          type: string
          description: Task ID to delete
      required:
        - id

  - name: get_task_summary
    description: Get aggregate task counts grouped by status and priority
    group: Analytics
    annotations:
      readOnlyHint: true
      idempotentHint: true
      openWorldHint: false

resources:
  - uri: tasks://summary
    name: task-summary
    mimeType: application/json

prompts:
  - name: task_report
    description: Generate a task status report for the current sprint
`;
