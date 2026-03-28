#!/usr/bin/env bash
# scan-secrets.sh — Scan content being written for credential patterns.
# Prints "ask" to trigger confirmation if a potential secret is detected.
# Does NOT hard-block — lets the user confirm (e.g., test fixtures).
# Exit 0 always.

set -euo pipefail

# Read the full stdin (tool input JSON)
INPUT=$(cat /dev/stdin)

# Extract the content being written.
# For Write tool: content field. For Edit tool: new_string field.
if command -v jq &>/dev/null; then
  CONTENT=$(echo "$INPUT" | jq -r '.content // .new_string // empty')
else
  # Without jq, we scan the entire input as a rough approximation
  CONTENT="$INPUT"
fi

# If no content to scan, allow
if [ -z "$CONTENT" ]; then
  exit 0
fi

FOUND=""

# AWS Access Key ID
if echo "$CONTENT" | grep -qE 'AKIA[A-Z0-9]{16}'; then
  FOUND="${FOUND}  - AWS Access Key ID pattern detected\n"
fi

# GitHub tokens
if echo "$CONTENT" | grep -qE 'gh[ps]_[A-Za-z0-9]{36,}'; then
  FOUND="${FOUND}  - GitHub token pattern detected\n"
fi

# OpenAI / Stripe-style API keys
if echo "$CONTENT" | grep -qE 'sk-[A-Za-z0-9]{20,}'; then
  FOUND="${FOUND}  - API key pattern (sk-...) detected\n"
fi

if echo "$CONTENT" | grep -qE 'sk_live_'; then
  FOUND="${FOUND}  - Stripe live key pattern detected\n"
fi

if echo "$CONTENT" | grep -qE 'sk_test_'; then
  FOUND="${FOUND}  - Stripe test key pattern detected\n"
fi

# Private key blocks
if echo "$CONTENT" | grep -qE '\-\-\-\-\-BEGIN.*PRIVATE KEY\-\-\-\-\-'; then
  FOUND="${FOUND}  - Private key block detected\n"
fi

# Database connection strings with embedded passwords
if echo "$CONTENT" | grep -qE '://[^[:space:]]+:[^[:space:]]+@'; then
  FOUND="${FOUND}  - Database connection string with credentials detected\n"
fi

if [ -n "$FOUND" ]; then
  echo "ask"
  echo "Potential secrets detected in content being written:"
  printf "$FOUND"
  echo "If this is intentional (e.g., test fixtures, documentation), confirm to proceed."
fi

exit 0
