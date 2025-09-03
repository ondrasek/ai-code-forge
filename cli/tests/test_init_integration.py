"""Integration tests for the init command template deployment functionality."""

import os
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from ai_code_forge_cli.cli import main


class TestInitIntegration:
    """Integration tests for acforge init command."""

    def test_init_happy_path_full_deployment(self, temp_repo):
        """Test successful full deployment with all files and directories."""
        runner = CliRunner()
        
        result = runner.invoke(main, [
            "init", str(temp_repo),
            "--project-name", "test-project",
            "--github-owner", "testuser"
        ])
        
        assert result.exit_code == 0
        assert "initialization complete" in result.output.lower()
        
        # Verify directory structure
        assert (temp_repo / ".acforge").is_dir()
        assert (temp_repo / ".devcontainer").is_dir()
        
        # Verify CLAUDE.md in root (not .acforge)
        claude_md = temp_repo / "CLAUDE.md"
        assert claude_md.exists()
        assert claude_md.is_file()
        
        # Verify key subdirectories in .acforge
        acforge_dir = temp_repo / ".acforge"
        for subdir in ["guidelines", "scripts", "mcp-servers", "prompts", "stacks", "readme"]:
            assert (acforge_dir / subdir).is_dir(), f"Missing {subdir} directory"
        
        # Verify state file created
        assert (acforge_dir / "state.json").exists()
        
        # Verify minimum file count (should be 140+)
        total_files = sum(1 for _ in temp_repo.rglob("*") if _.is_file())
        assert total_files >= 140, f"Expected 140+ files, got {total_files}"

    def test_init_dry_run_no_files_created(self, temp_repo):
        """Test dry-run mode creates no files but shows what would be created."""
        runner = CliRunner()
        
        result = runner.invoke(main, [
            "init", str(temp_repo), "--dry-run",
            "--project-name", "test-project", 
            "--github-owner", "testuser"
        ])
        
        assert result.exit_code == 0
        assert "dry run" in result.output.lower()
        assert "would be created" in result.output.lower()
        
        # Verify no actual files created
        assert not (temp_repo / ".acforge").exists()
        assert not (temp_repo / "CLAUDE.md").exists()
        assert not (temp_repo / ".devcontainer").exists()
        
        # But should show comprehensive file list
        assert ".acforge/guidelines" in result.output
        assert ".acforge/scripts" in result.output
        assert "CLAUDE.md" in result.output

    def test_claude_md_parameter_substitution(self, temp_repo):
        """Test that CLAUDE.md gets proper parameter substitution."""
        runner = CliRunner()
        
        result = runner.invoke(main, [
            "init", str(temp_repo),
            "--project-name", "my-awesome-project",
            "--github-owner", "awesomedev"
        ])
        
        assert result.exit_code == 0
        
        claude_md = temp_repo / "CLAUDE.md"
        content = claude_md.read_text()
        
        # Verify parameters were substituted
        assert "awesomedev" in content
        assert "my-awesome-project" in content
        
        # Verify it's not in .acforge (special case handling)
        assert not (temp_repo / ".acforge" / "CLAUDE.md").exists()

    def test_init_force_overwrites_existing(self, existing_acf_config):
        """Test --force flag overwrites existing configuration."""
        # Add a test file to existing config
        test_file = existing_acf_config / ".acforge" / "test_file.txt"
        test_file.write_text("original content")
        
        runner = CliRunner()
        result = runner.invoke(main, [
            "init", str(existing_acf_config), "--force",
            "--project-name", "test-project",
            "--github-owner", "testuser"
        ])
        
        assert result.exit_code == 0
        assert "initialization complete" in result.output.lower()
        
        # Verify new deployment happened (overwrites old config)
        state_file = existing_acf_config / ".acforge" / "state.json"
        assert state_file.exists()
        
        # Verify parameters were applied in deployed files
        claude_md = existing_acf_config / "CLAUDE.md"
        assert claude_md.exists()
        claude_content = claude_md.read_text()
        assert "test-project" in claude_content or "testuser" in claude_content

    def test_init_detects_existing_config_without_force(self, existing_acf_config):
        """Test that init refuses to overwrite existing config without --force."""
        runner = CliRunner()
        
        result = runner.invoke(main, [
            "init", str(existing_acf_config),
            "--project-name", "test-project",
            "--github-owner", "testuser"
        ])
        
        assert result.exit_code != 0
        assert "already has" in result.output.lower() or "existing" in result.output.lower()

    def test_devcontainer_scripts_executable(self, temp_repo):
        """Test that DevContainer shell scripts get executable permissions."""
        runner = CliRunner()
        
        result = runner.invoke(main, [
            "init", str(temp_repo),
            "--project-name", "test-project",
            "--github-owner", "testuser"
        ])
        
        assert result.exit_code == 0
        
        # Find shell scripts in .devcontainer
        devcontainer_dir = temp_repo / ".devcontainer"
        shell_scripts = list(devcontainer_dir.rglob("*.sh"))
        
        assert len(shell_scripts) > 0, "No shell scripts found in .devcontainer"
        
        # Verify they're executable
        for script in shell_scripts:
            stat_info = script.stat()
            assert stat_info.st_mode & 0o111, f"Script {script.name} is not executable"

    def test_static_content_deployment(self, temp_repo):
        """Test that static content (scripts, mcp-servers) is deployed correctly."""
        runner = CliRunner()
        
        result = runner.invoke(main, [
            "init", str(temp_repo),
            "--project-name", "test-project",
            "--github-owner", "testuser"
        ])
        
        assert result.exit_code == 0
        
        # Verify scripts directory structure
        scripts_dir = temp_repo / ".acforge" / "scripts"
        assert scripts_dir.is_dir()
        assert (scripts_dir / "launch-claude.sh").exists()
        assert (scripts_dir / "worktree").is_dir()
        
        # Verify MCP servers
        mcp_dir = temp_repo / ".acforge" / "mcp-servers"
        assert mcp_dir.is_dir()
        assert (mcp_dir / "mcp-config.json").exists()
        assert (mcp_dir / "openai-structured-mcp").is_dir()
        assert (mcp_dir / "perplexity-mcp").is_dir()

    def test_missing_required_parameters_uses_defaults(self, temp_repo):
        """Test behavior when required parameters are not provided."""
        runner = CliRunner()
        
        # Run without explicit parameters
        result = runner.invoke(main, ["init", str(temp_repo)])
        
        # Should still succeed (uses defaults or detection)
        assert result.exit_code == 0
        assert (temp_repo / "CLAUDE.md").exists()
        
        # Check that CLAUDE.md has some parameter placeholders or defaults
        content = (temp_repo / "CLAUDE.md").read_text()
        # Should have either substituted values or preserved placeholders
        assert len(content) > 1000, "CLAUDE.md seems too short - may have failed substitution"


class TestEdgeCases:
    """Edge case testing for robustness."""

    def test_init_in_readonly_directory(self):
        """Test behavior when target directory is read-only."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Make directory read-only
            temp_path.chmod(0o444)
            
            try:
                runner = CliRunner()
                result = runner.invoke(main, [
                    "init", str(temp_path),
                    "--project-name", "test-project",
                    "--github-owner", "testuser"
                ])
                
                # Should fail gracefully
                assert result.exit_code != 0
                assert "permission" in result.output.lower() or "error" in result.output.lower()
                
            finally:
                # Restore permissions for cleanup
                temp_path.chmod(0o755)

    def test_init_with_special_characters_in_parameters(self, temp_repo):
        """Test parameter substitution with special characters."""
        runner = CliRunner()
        
        result = runner.invoke(main, [
            "init", str(temp_repo),
            "--project-name", "test-project_with-special.chars",
            "--github-owner", "user@domain.com"
        ])
        
        # Should handle special characters gracefully
        assert result.exit_code == 0
        
        content = (temp_repo / "CLAUDE.md").read_text()
        assert "test-project_with-special.chars" in content
        assert "user@domain.com" in content

    def test_deployment_file_count_validation(self, temp_repo):
        """Validate that deployment includes expected minimum file count."""
        runner = CliRunner()
        
        result = runner.invoke(main, [
            "init", str(temp_repo),
            "--project-name", "test-project",
            "--github-owner", "testuser"
        ])
        
        assert result.exit_code == 0
        
        # Count files in each major directory
        acforge_files = len(list((temp_repo / ".acforge").rglob("*")))
        devcontainer_files = len(list((temp_repo / ".devcontainer").rglob("*")))
        
        # Validate reasonable file counts
        assert acforge_files >= 100, f"Expected 100+ files in .acforge, got {acforge_files}"
        assert devcontainer_files >= 20, f"Expected 20+ files in .devcontainer, got {devcontainer_files}"
        
        # Verify specific critical files exist
        critical_files = [
            ".acforge/state.json",
            ".acforge/guidelines/CLAUDE.md", 
            ".acforge/scripts/launch-claude.sh",
            ".devcontainer/devcontainer.json",
            "CLAUDE.md"
        ]
        
        for critical_file in critical_files:
            assert (temp_repo / critical_file).exists(), f"Critical file missing: {critical_file}"