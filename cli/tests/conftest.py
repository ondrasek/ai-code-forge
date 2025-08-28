"""Test configuration and fixtures."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_repo():
    """Create a temporary directory for testing repository operations."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def git_repo(temp_repo):
    """Create a temporary git repository."""
    (temp_repo / ".git").mkdir()
    return temp_repo


@pytest.fixture
def existing_claude_config(temp_repo):
    """Create a repository with existing .claude configuration."""
    claude_dir = temp_repo / ".claude"
    claude_dir.mkdir()
    (claude_dir / "settings.json").write_text("{}")
    return temp_repo


@pytest.fixture
def existing_acf_config(temp_repo):
    """Create a repository with existing .acf configuration."""
    acf_dir = temp_repo / ".acf"
    acf_dir.mkdir()
    (acf_dir / "state.json").write_text("{}")
    return temp_repo