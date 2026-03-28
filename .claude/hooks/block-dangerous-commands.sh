#!/usr/bin/env bash
# block-dangerous-commands.sh — Block dangerous shell commands.
# Exit 0 = allow, exit 2 = block.

set -euo pipefail

# Extract the command from the tool input.
if command -v jq &>/dev/null; then
  COMMAND=$(cat /dev/stdin | jq -r '.command // empty')
else
  COMMAND=$(cat /dev/stdin | grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"command"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
fi

# If we couldn't extract a command, allow
if [ -z "$COMMAND" ]; then
  exit 0
fi

# BLOCK: Force-push to main/master (but allow --force-with-lease)
if echo "$COMMAND" | grep -qE 'git\s+push\s+.*--force\b' && \
   echo "$COMMAND" | grep -qE '\b(main|master)\b' && \
   ! echo "$COMMAND" | grep -qE '--force-with-lease'; then
  echo "BLOCKED: Force-pushing to main/master is not allowed. Use --force-with-lease instead."
  exit 2
fi

# BLOCK: Destructive rm commands
if echo "$COMMAND" | grep -qE 'rm\s+-rf\s+/\s' || echo "$COMMAND" | grep -qE 'rm\s+-rf\s+/$'; then
  echo "BLOCKED: 'rm -rf /' is not allowed."
  exit 2
fi

if echo "$COMMAND" | grep -qE 'rm\s+-rf\s+~'; then
  echo "BLOCKED: 'rm -rf ~' is not allowed."
  exit 2
fi

if echo "$COMMAND" | grep -qE 'rm\s+-rf\s+\.\.'; then
  echo "BLOCKED: 'rm -rf ..' is not allowed."
  exit 2
fi

# BLOCK: Dangerous SQL operations
if echo "$COMMAND" | grep -qiE 'DROP\s+TABLE'; then
  echo "BLOCKED: DROP TABLE is not allowed."
  exit 2
fi

if echo "$COMMAND" | grep -qiE 'DROP\s+DATABASE'; then
  echo "BLOCKED: DROP DATABASE is not allowed."
  exit 2
fi

if echo "$COMMAND" | grep -qiE 'DELETE\s+FROM' && ! echo "$COMMAND" | grep -qiE 'WHERE'; then
  echo "BLOCKED: DELETE FROM without WHERE clause is not allowed."
  exit 2
fi

if echo "$COMMAND" | grep -qiE 'TRUNCATE'; then
  echo "BLOCKED: TRUNCATE is not allowed."
  exit 2
fi

# BLOCK: Insecure permission and piped execution
if echo "$COMMAND" | grep -qE 'chmod\s+777'; then
  echo "BLOCKED: 'chmod 777' is not allowed. Use more restrictive permissions."
  exit 2
fi

if echo "$COMMAND" | grep -qE 'curl\s.*\|\s*(sh|bash)' || echo "$COMMAND" | grep -qE 'curl\s.*\|\s*(sh|bash)'; then
  echo "BLOCKED: Piping curl output to shell is not allowed."
  exit 2
fi

# ALLOW: Everything else
exit 0
