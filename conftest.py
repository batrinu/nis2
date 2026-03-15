"""
Root conftest file for NIS2 Compliance Assessment System.
"""
import pytest

# Configure anyio for async tests
pytest_plugins = ['anyio']

@pytest.fixture
def anyio_backend() -> str:
    """Return the async backend to use for anyio tests."""
    return "asyncio"
