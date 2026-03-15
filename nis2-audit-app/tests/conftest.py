"""
# Shared fixtures and configuration for pytest.

This module provides common fixtures and configuration for all tests
in the nis2-audit-app test suite.
"""
import pytest
import os
import shutil
from pathlib import Path


@pytest.fixture(autouse=True)

def setup_test_env() -> None:
    """Set up test environment variables for all tests."""
    # Set a test database path
    os.environ['NIS2_TESTING'] = '1'
    os.environ['TERM'] = 'xterm-256color'
    yield
    # Cleanup after tests
    if 'NIS2_TESTING' in os.environ:
        del os.environ['NIS2_TESTING']


@pytest.fixture
def clean_config() -> None:
    """Remove config directory for fresh start tests."""
    config_dir = Path.home() / ".nis2-audit"
    if config_dir.exists():
        shutil.rmtree(config_dir)
    yield
    # Cleanup after test
    if config_dir.exists():
        shutil.rmtree(config_dir)


@pytest.fixture
def app() -> "NIS2AuditApp":
    """Create and return a fresh NIS2AuditApp instance for testing."""
    from app.textual_app import NIS2AuditApp
    return NIS2AuditApp()
