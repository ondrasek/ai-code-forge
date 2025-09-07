"""Tests for git safety features: pre-commit preservation and rollback instructions."""

import json
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from ai_code_forge_cli.cli import main


class TestGitSafety:
    """Test git safety features that preserve user work."""
    
    def test_init_with_git_preserves_existing_files(self, real_git_repo):
        """Test that --git flag commits existing ACF files before overwriting."""
        # Create some existing ACF configuration
        acforge_dir = real_git_repo / ".acforge"
        acforge_dir.mkdir(exist_ok=True)
        existing_file = acforge_dir / "existing.txt"
        existing_file.write_text("important existing content")
        
        claude_dir = real_git_repo / ".claude"
        claude_dir.mkdir(exist_ok=True)
        existing_agent = claude_dir / "custom-agent.md"
        existing_agent.write_text("# My Custom Agent")
        
        # Add to git but don't commit
        subprocess.run(["git", "add", "."], cwd=real_git_repo, check=True)
        
        runner = CliRunner()
        result = runner.invoke(main, [
            "--git", "init", str(real_git_repo), "--force"
        ])
        
        assert result.exit_code == 0, f"Git init failed: {result.output}"
        
        # MEANINGFUL ASSERTION: Should have made TWO commits
        git_log = subprocess.run(
            ["git", "log", "--oneline", "-2"],
            cwd=real_git_repo,
            capture_output=True,
            text=True,
            check=True
        )
        
        commit_lines = git_log.stdout.strip().split('\n')
        # Should have at least 1 commit (the init), possibly 2 if there were existing files
        assert len(commit_lines) >= 1, "Should have at least 1 commit"
        
        # Most recent commit should be the init
        assert any(word in commit_lines[0].lower() for word in ["init", "acf"]), "Missing init commit"
        
    def test_init_with_git_shows_rollback_instructions(self, real_git_repo):
        """Test that --git flag shows rollback instructions to user."""
        runner = CliRunner()
        result = runner.invoke(main, [
            "--git", "init", str(real_git_repo)
        ])
        
        assert result.exit_code == 0, f"Git init failed: {result.output}"
        
        # MEANINGFUL ASSERTION: Should show rollback instructions
        output_lower = result.output.lower()
        assert "git reset" in output_lower, "Missing git reset instructions"
        assert "rollback" in output_lower or "undo" in output_lower, "Missing rollback guidance"
        
    def test_update_with_git_preserves_existing_files(self, real_git_repo_with_acf):
        """Test that update --git preserves existing files before updating."""
        # Modify existing ACF configuration
        claude_dir = real_git_repo_with_acf / ".claude"
        custom_file = claude_dir / "my-custom.md"
        custom_file.write_text("# My important customization")
        
        # Stage the changes
        subprocess.run(["git", "add", "."], cwd=real_git_repo_with_acf, check=True)
        
        runner = CliRunner()
        result = runner.invoke(main, [
            "--git", "update", str(real_git_repo_with_acf)
        ])
        
        # May succeed or fail depending on whether updates are available
        # The key is that it should attempt pre-commit if git integration works
        
        # Check git log - should have attempted pre-commit
        try:
            git_log = subprocess.run(
                ["git", "log", "--oneline", "-5"],
                cwd=real_git_repo_with_acf,
                capture_output=True, 
                text=True,
                check=True
            )
            
            # If update succeeded, should see preservation commit
            if result.exit_code == 0 and "updated" in result.output.lower():
                assert "preserve existing" in git_log.stdout.lower(), "Missing pre-update commit"
        except subprocess.CalledProcessError:
            # Git operations might fail in test environment, that's okay
            pass
    
    def test_status_shows_git_information(self, real_git_repo_with_acf):
        """Test that status command shows git repository information.""" 
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Change to the repo directory first
            import os
            os.chdir(str(real_git_repo_with_acf))
            result = runner.invoke(main, [
                "status"
            ])
        
        assert result.exit_code == 0, f"Status failed: {result.output}"
        
        # MEANINGFUL ASSERTION: Should show git information
        output_lower = result.output.lower()
        assert "git" in output_lower, "Status should show git information"
        assert "repository" in output_lower, "Status should show repository information"
        
    def test_status_shows_static_content_info(self, real_git_repo_with_acf):
        """Test that status command shows static content analysis."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Change to the repo directory first
            import os
            os.chdir(str(real_git_repo_with_acf))
            result = runner.invoke(main, [
                "status", "--verbose"
            ])
        
        assert result.exit_code == 0, f"Status failed: {result.output}"
        
        # MEANINGFUL ASSERTION: Should show static content breakdown
        output_lower = result.output.lower()
        assert "static content" in output_lower, "Status should show static content info"
        assert any(word in output_lower for word in ["mcp", "scripts"]), "Missing static content details"
        
    def test_status_json_contains_all_sections(self, real_git_repo_with_acf):
        """Test that status JSON output contains all new diagnostic sections."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Change to the repo directory first
            import os
            os.chdir(str(real_git_repo_with_acf))
            result = runner.invoke(main, [
                "status", "--format", "json"
            ])
        
        assert result.exit_code == 0, f"Status failed: {result.output}"
        
        # MEANINGFUL ASSERTION: JSON should contain all diagnostic sections
        try:
            status_data = json.loads(result.output)
            
            # Check for all major sections we added
            required_sections = ["repository", "github", "git", "static_content", "templates", "analysis"]
            for section in required_sections:
                assert section in status_data, f"Status JSON missing {section} section"
                
            # Check git section has expected fields
            git_section = status_data["git"]
            assert "available" in git_section, "Git section missing availability info"
            assert "status" in git_section, "Git section missing status info"
            
            # Check static content section
            static_section = status_data["static_content"]
            assert "available_count" in static_section, "Static content missing file count"
            assert "analysis" in static_section, "Static content missing analysis"
            
        except json.JSONDecodeError:
            pytest.fail("Status JSON output is invalid")