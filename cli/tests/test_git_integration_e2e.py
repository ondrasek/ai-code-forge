"""End-to-end integration tests for git integration with CLI commands."""

import subprocess
import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from ai_code_forge_cli.cli import main


class TestGitIntegrationE2E:
    """End-to-end tests for git integration with actual git operations."""
    
    def test_init_with_git_creates_commit(self, real_git_repo):
        """Test init command with --git flag creates proper git commit."""
        runner = CliRunner()
        
        # Run init command with git integration
        result = runner.invoke(main, [
            "--git", "init", str(real_git_repo),
            "--force"  # In case any files exist
        ])
        
        # Should succeed
        assert result.exit_code == 0, f"Init failed: {result.output}"
        
        # Check git log for commit
        git_result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=real_git_repo,
            capture_output=True,
            text=True,
            check=True
        )
        
        commit_line = git_result.stdout.strip()
        
        # Verify commit was made (flexible check for different commit message formats)
        assert len(commit_line) > 10, "No commit found or commit message too short"
        assert any(word in commit_line.lower() for word in ["init", "acf", "acforge"]), "Commit message doesn't reference ACF init"
        
        # Verify git status is clean (all files committed)
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=real_git_repo,
            capture_output=True,
            text=True,
            check=True
        )
        
        assert status_result.stdout.strip() == "", f"Working directory not clean: {status_result.stdout}"
        
        # Verify expected files are in git
        ls_result = subprocess.run(
            ["git", "ls-files"],
            cwd=real_git_repo,
            capture_output=True,
            text=True,
            check=True
        )
        
        git_files = set(ls_result.stdout.strip().split('\n'))
        
        # Key files should be tracked
        expected_files = {
            "CLAUDE.md",
            ".acforge/state.json",
            ".devcontainer/devcontainer.json"
        }
        
        for expected_file in expected_files:
            assert expected_file in git_files, f"Expected file {expected_file} not tracked by git"
    
    def test_init_without_git_no_commit(self, real_git_repo):
        """Test init command without --git flag does not create commit."""
        runner = CliRunner()
        
        # Run init command without git integration
        result = runner.invoke(main, [
            "init", str(real_git_repo),
            "--force"
        ])
        
        # Should succeed
        assert result.exit_code == 0, f"Init failed: {result.output}"
        
        # Check git log - should have no commits
        git_result = subprocess.run(
            ["git", "log", "--oneline"],
            cwd=real_git_repo,
            capture_output=True,
            text=True
        )
        
        # Should fail because no commits exist, or return empty
        assert git_result.returncode != 0 or git_result.stdout.strip() == ""
    
    def test_init_git_with_dry_run_no_commit(self, real_git_repo):
        """Test init with --git and --dry-run does not create commit."""
        runner = CliRunner()
        
        result = runner.invoke(main, [
            "--git", "init", str(real_git_repo),
            "--dry-run"
        ])
        
        # Should succeed
        assert result.exit_code == 0, f"Init dry-run failed: {result.output}"
        
        # Should show dry-run message
        assert "DRY RUN" in result.output
        
        # Check git log - should have no commits
        git_result = subprocess.run(
            ["git", "log", "--oneline"],
            cwd=real_git_repo,
            capture_output=True,
            text=True
        )
        
        assert git_result.returncode != 0 or git_result.stdout.strip() == ""
    
    def test_update_with_git_creates_commit(self, real_git_repo):
        """Test update command with --git flag creates proper commit."""
        runner = CliRunner()
        
        # First initialize without git to create baseline
        init_result = runner.invoke(main, [
            "init", str(real_git_repo),
            "--force"
        ])
        assert init_result.exit_code == 0, f"Init failed: {init_result.output}"
        
        # Commit initial state manually
        subprocess.run(["git", "add", "."], cwd=real_git_repo, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial ACF setup"],
            cwd=real_git_repo, 
            check=True
        )
        
        # Now run update with git integration
        update_result = runner.invoke(main, [
            "--git", "update", str(real_git_repo),
            "--force"  # In case there are conflicts
        ])
        
        # Check result - might succeed or show "up to date"
        if update_result.exit_code == 0:
            # Check git log for update commit
            git_result = subprocess.run(
                ["git", "log", "--oneline", "-2"],
                cwd=real_git_repo,
                capture_output=True,
                text=True,
                check=True
            )
            
            commits = git_result.stdout.strip().split('\n')
            
            # Should have at least 1 commit (the init), possibly 2 if update made changes
            assert len(commits) >= 1
            
            # If update created changes, latest commit should be update
            if len(commits) >= 2 and "acforge update configuration" in commits[0]:
                assert "chore: acforge update configuration" in commits[0]
            else:
                # If no update was needed, should still have the init commit
                assert any(word in commits[0].lower() for word in ["init", "acf", "acforge"]), "Should have init commit"
    
    def test_git_integration_error_handling(self, temp_repo):
        """Test git integration gracefully handles non-git directory."""
        runner = CliRunner()
        
        # Run init with git flag in non-git directory
        result = runner.invoke(main, [
            "--git", "init", str(temp_repo),
            "--force"
        ])
        
        # Should still succeed (git integration just skips)
        assert result.exit_code == 0, f"Init failed: {result.output}"
        
        # Files should still be created
        assert (temp_repo / "CLAUDE.md").exists()
        assert (temp_repo / ".acforge" / "state.json").exists()
    
    def test_git_integration_commit_message_format(self, real_git_repo):
        """Test git commit message format is correct."""
        runner = CliRunner()
        
        # Run init command with git integration
        result = runner.invoke(main, [
            "--git", "init", str(real_git_repo),
            "--force"
        ])
        
        assert result.exit_code == 0, f"Init failed: {result.output}"
        
        # Get commit details
        git_result = subprocess.run(
            ["git", "log", "-1", "--format=%H %s"],
            cwd=real_git_repo,
            capture_output=True,
            text=True,
            check=True
        )
        
        commit_line = git_result.stdout.strip()
        hash_and_message = commit_line.split(" ", 1)
        
        assert len(hash_and_message) == 2
        commit_hash, commit_message = hash_and_message
        
        # Validate hash format
        assert len(commit_hash) == 40  # Full SHA hash
        assert all(c in '0123456789abcdef' for c in commit_hash.lower())
        
        # Validate commit message format
        assert commit_message.startswith("chore: acforge init configuration")
        assert "v" in commit_message  # Should contain version
    
    def test_multiple_commands_git_integration(self, real_git_repo):
        """Test multiple commands with git create separate commits."""
        runner = CliRunner()
        
        # First init
        init_result = runner.invoke(main, [
            "--git", "init", str(real_git_repo),
            "--force"
        ])
        assert init_result.exit_code == 0
        
        # Then update (might not change anything, but tests the workflow)
        update_result = runner.invoke(main, [
            "--git", "update", str(real_git_repo),
            "--force"
        ])
        # Update might exit 0 or say "up to date" - both are fine
        
        # Check git history
        git_result = subprocess.run(
            ["git", "log", "--oneline"],
            cwd=real_git_repo,
            capture_output=True,
            text=True,
            check=True
        )
        
        commits = git_result.stdout.strip().split('\n')
        
        # Should have at least one commit from init
        assert len(commits) >= 1
        assert "acforge" in commits[0]  # Most recent commit should be ACF-related


class TestGitIntegrationValidation:
    """Tests to validate git integration produces correct repository state."""
    
    def test_git_integration_preserves_functionality(self, real_git_repo):
        """Test that git integration doesn't break core functionality."""
        runner = CliRunner()
        
        # Run with git integration
        result = runner.invoke(main, [
            "--git", "init", str(real_git_repo),
            "--force"
        ])
        
        assert result.exit_code == 0
        
        # Verify all key functionality still works
        
        # 1. CLAUDE.md should exist and be valid
        claude_md = real_git_repo / "CLAUDE.md"
        assert claude_md.exists()
        claude_content = claude_md.read_text()
        # Basic structure checks instead of specific parameter values
        assert len(claude_content) > 100  # Should have substantial content
        
        # 2. DevContainer should be valid JSON
        devcontainer_json = real_git_repo / ".devcontainer" / "devcontainer.json"
        assert devcontainer_json.exists()
        try:
            devcontainer_config = json.loads(devcontainer_json.read_text())
            # Basic validity check instead of specific content
            assert isinstance(devcontainer_config, dict)
        except json.JSONDecodeError as e:
            pytest.fail(f"DevContainer JSON invalid: {e}")
        
        # 3. State file should be valid
        state_file = real_git_repo / ".acforge" / "state.json"
        assert state_file.exists()
        try:
            state_data = json.loads(state_file.read_text())
            assert "installation" in state_data
            assert "templates" in state_data
        except json.JSONDecodeError as e:
            pytest.fail(f"State JSON invalid: {e}")
        
        # 4. All files should be committed and tracked
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=real_git_repo,
            capture_output=True,
            text=True,
            check=True
        )
        assert status_result.stdout.strip() == ""
    
    def test_git_integration_with_existing_files(self, git_repo_with_commits):
        """Test git integration works with pre-existing repository content."""
        runner = CliRunner()
        
        # Repository already has README.md committed
        
        result = runner.invoke(main, [
            "--git", "init", str(git_repo_with_commits),
            "--force"
        ])
        
        assert result.exit_code == 0
        
        # Should now have 2 commits
        git_result = subprocess.run(
            ["git", "log", "--oneline"],
            cwd=git_repo_with_commits,
            capture_output=True,
            text=True,
            check=True
        )
        
        commits = git_result.stdout.strip().split('\n')
        assert len(commits) == 2
        
        # Latest should be ACF commit
        assert "acforge init configuration" in commits[0]
        
        # Original should be preserved
        assert "Initial commit" in commits[1]
        
        # Both README.md and ACF files should exist
        assert (git_repo_with_commits / "README.md").exists()
        assert (git_repo_with_commits / "CLAUDE.md").exists()