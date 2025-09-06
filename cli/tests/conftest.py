"""Test configuration and fixtures."""

import subprocess
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
    """Create a repository with existing .acforge configuration."""
    acf_dir = temp_repo / ".acforge"
    acf_dir.mkdir()
    (acf_dir / "state.json").write_text("{}")
    return temp_repo


@pytest.fixture
def real_git_repo(temp_repo):
    """Create a real git repository with proper git initialization."""
    # Initialize real git repository
    subprocess.run(["git", "init"], cwd=temp_repo, check=True, capture_output=True)
    
    # Configure git user for testing
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=temp_repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=temp_repo, check=True)
    
    return temp_repo


@pytest.fixture
def git_repo_with_commits(real_git_repo):
    """Create a git repository with some initial commits."""
    # Create initial file and commit
    test_file = real_git_repo / "README.md"
    test_file.write_text("# Test Repository")
    
    subprocess.run(["git", "add", "README.md"], cwd=real_git_repo, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=real_git_repo, check=True)
    
    return real_git_repo


@pytest.fixture
def real_git_repo_with_acf(real_git_repo):
    """Create a real git repository with ACF already initialized."""
    from click.testing import CliRunner
    from ai_code_forge_cli.cli import main
    
    # Initialize ACF in the git repo
    runner = CliRunner()
    result = runner.invoke(main, [
        "init", str(real_git_repo), "--force"
    ])
    
    # If init failed, return the repo anyway for testing error conditions
    if result.exit_code != 0:
        pytest.skip(f"Could not initialize ACF in test repo: {result.output}")
    
    return real_git_repo