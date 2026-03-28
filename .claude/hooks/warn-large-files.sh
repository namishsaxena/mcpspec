#!/usr/bin/env bash
# warn-large-files.sh — Warn when a file exceeds 300 lines after write/edit.
# This hook never blocks — it only prints a warning.
# Exit 0 always.

set -euo pipefail

LINE_LIMIT=300

# Extract the file path from the tool input.
if command -v jq &>/dev/null; then
  FILE_PATH=$(cat /dev/stdin | jq -r '.file_path // empty')
else
  FILE_PATH=$(cat /dev/stdin | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
fi

# If we couldn't extract a file path, skip
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

BASENAME=$(basename "$FILE_PATH")

# Skip: test files, markdown, JSON — these are expected to be longer
case "$BASENAME" in
  *.test.ts|*.test.js|*.spec.ts|*.spec.js)
    exit 0
    ;;
  test_*.py)
    exit 0
    ;;
  *.md|*.json)
    exit 0
    ;;
esac

# Check if the file exists and count lines
if [ -f "$FILE_PATH" ]; then
  LINES=$(wc -l < "$FILE_PATH" | tr -d ' ')
  if [ "$LINES" -gt "$LINE_LIMIT" ]; then
    echo "WARNING: $FILE_PATH has $LINES lines (limit: $LINE_LIMIT). Consider refactoring."
  fi
fi

exit 0
