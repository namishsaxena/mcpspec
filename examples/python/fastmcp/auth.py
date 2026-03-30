"""Bearer token auth for the Task Manager example.

Protects /mcp only — /docs and /mcpspec.yaml stay public.
Uses hmac.compare_digest for timing-safe comparison.
"""

import hmac
import os

API_TOKEN = os.environ.get("API_TOKEN", "mcpspec-demo-token")


def verify_token(token: str) -> bool:
    """Verify a bearer token using timing-safe comparison."""
    return hmac.compare_digest(token, API_TOKEN)


def extract_bearer_token(authorization: str | None) -> str | None:
    """Extract the token from an Authorization: Bearer header."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    return authorization[7:]
