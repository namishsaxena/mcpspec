"""Shared test configuration for mcpspec-dev."""

import pytest


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"
