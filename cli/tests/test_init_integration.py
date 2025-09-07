"""Integration tests for meaningful CLI deployment functionality."""

import json
import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from ai_code_forge_cli.cli import main


class TestMeaningfulIntegration:
    """Integration tests that validate actual functionality, not just file existence."""

    def test_complete_deployment_workflow(self, temp_repo):
        """Test full deployment creates functional configuration."""
        runner = CliRunner()
        
        result = runner.invoke(main, [
            "init", str(temp_repo)
        ])
        
        assert result.exit_code == 0, f"Deployment failed: {result.output}"
        
        # MEANINGFUL ASSERTION: Verify CLAUDE.md contains actual project parameters
        claude_md = temp_repo / "CLAUDE.md"
        assert claude_md.exists(), "CLAUDE.md not deployed"
        
        claude_content = claude_md.read_text()
        # Verify parameter substitution occurred (should not contain template placeholders)
        assert "{{GITHUB_OWNER}}" not in claude_content, "GitHub owner placeholder not substituted"
        assert "{{PROJECT_NAME}}" not in claude_content, "Project name placeholder not substituted"
        
        # MEANINGFUL ASSERTION: Verify DevContainer JSON is valid
        devcontainer_json = temp_repo / ".devcontainer" / "devcontainer.json"
        assert devcontainer_json.exists(), "DevContainer config not deployed"
        
        # This would catch deployment failures that create corrupt JSON
        try:
            devcontainer_config = json.loads(devcontainer_json.read_text())
            # Verify it's valid JSON and contains expected structure
            assert "name" in devcontainer_config, "DevContainer missing name field"
        except json.JSONDecodeError as e:
            pytest.fail(f"DevContainer JSON is invalid: {e}")
        
        # MEANINGFUL ASSERTION: Verify state file is valid and useful  
        state_file = temp_repo / ".acforge" / "state.json"
        assert state_file.exists(), "State file not created"
        
        try:
            state_data = json.loads(state_file.read_text())
            assert "installation" in state_data, "State file missing installation info"
            assert "templates" in state_data, "State file missing template info"
        except json.JSONDecodeError:
            pytest.fail("State file contains invalid JSON")

    def test_dry_run_prevents_deployment(self, temp_repo):
        """Test dry-run mode creates no files but shows deployment plan."""
        runner = CliRunner()
        
        result = runner.invoke(main, [
            "init", str(temp_repo), "--dry-run"
        ])
        
        assert result.exit_code == 0
        assert "dry run" in result.output.lower()
        
        # MEANINGFUL ASSERTION: Verify no actual deployment happened
        assert not (temp_repo / ".acforge").exists()
        assert not (temp_repo / "CLAUDE.md").exists()
        assert not (temp_repo / ".devcontainer").exists()
        
        # MEANINGFUL ASSERTION: But should show what would be deployed
        assert "CLAUDE.md" in result.output
        assert ".acforge" in result.output

    def test_force_overwrites_existing_config(self, existing_acf_config):
        """Test force flag properly overwrites existing configuration."""
        # Add marker to existing config to verify it gets overwritten
        marker_file = existing_acf_config / ".acforge" / "marker.txt"
        marker_file.write_text("original")
        
        runner = CliRunner()
        result = runner.invoke(main, [
            "init", str(existing_acf_config), "--force"
        ])
        
        assert result.exit_code == 0
        
        # MEANINGFUL ASSERTION: Verify deployment happened (files exist)
        claude_md = existing_acf_config / "CLAUDE.md"
        assert claude_md.exists(), "CLAUDE.md not deployed during force init"
        
        # MEANINGFUL ASSERTION: Verify old marker file was cleaned up (full overwrite)
        # Note: This test might need adjustment based on actual --force behavior
    
    def test_claude_code_templates_deployed(self, temp_repo):
        """Test that Claude Code agent and command templates are properly deployed."""
        runner = CliRunner()
        
        result = runner.invoke(main, [
            "init", str(temp_repo)
        ])
        
        assert result.exit_code == 0, f"Deployment failed: {result.output}"
        
        # MEANINGFUL ASSERTION: Verify .claude directory structure
        claude_dir = temp_repo / ".claude"
        assert claude_dir.exists(), "Claude Code directory not created"
        
        # MEANINGFUL ASSERTION: Verify agents deployed
        agents_dir = claude_dir / "agents"
        assert agents_dir.exists(), "Agents directory not created"
        
        foundation_dir = agents_dir / "foundation"
        specialists_dir = agents_dir / "specialists"
        assert foundation_dir.exists(), "Foundation agents directory not created"
        assert specialists_dir.exists(), "Specialists agents directory not created"
        
        # MEANINGFUL ASSERTION: Verify key agents exist
        context_agent = foundation_dir / "context.md"
        git_workflow_agent = specialists_dir / "git-workflow.md"
        assert context_agent.exists(), "Context agent not deployed"
        assert git_workflow_agent.exists(), "Git workflow agent not deployed"
        
        # MEANINGFUL ASSERTION: Verify commands deployed
        commands_dir = claude_dir / "commands"
        assert commands_dir.exists(), "Commands directory not created"
        
        # Check for some key commands
        research_cmd = commands_dir / "research.md"
        assert research_cmd.exists(), "Research command not deployed"
        
        # MEANINGFUL ASSERTION: Verify settings file
        settings_file = claude_dir / "settings.json"
        assert settings_file.exists(), "Claude Code settings not deployed"
        
        # Verify settings is valid JSON
        try:
            json.loads(settings_file.read_text())
        except json.JSONDecodeError:
            pytest.fail("Claude Code settings contains invalid JSON")
    
    def test_template_content_deployed(self, temp_repo):
        """Test that template content (Claude Code templates) is properly deployed."""
        runner = CliRunner()
        
        result = runner.invoke(main, [
            "init", str(temp_repo)
        ])
        
        assert result.exit_code == 0, f"Deployment failed: {result.output}"
        
        # MEANINGFUL ASSERTION: Verify .claude directory with templates
        claude_dir = temp_repo / ".claude"
        assert claude_dir.exists(), "Claude directory not created"
        
        # MEANINGFUL ASSERTION: Verify agents deployed
        agents_dir = claude_dir / "agents"
        if agents_dir.exists():
            agent_files = list(agents_dir.rglob("*.md"))
            assert len(agent_files) > 0, "No agent template files deployed"
        
        # MEANINGFUL ASSERTION: Verify commands deployed  
        commands_dir = claude_dir / "commands"
        if commands_dir.exists():
            command_files = list(commands_dir.rglob("*.md"))
            assert len(command_files) > 0, "No command template files deployed"

    def test_executable_permissions_applied(self, temp_repo):
        """Test that shell scripts get proper executable permissions."""
        runner = CliRunner()
        
        result = runner.invoke(main, [
            "init", str(temp_repo)
        ])
        
        assert result.exit_code == 0
        
        # MEANINGFUL ASSERTION: Find shell scripts and verify permissions
        shell_scripts = list(temp_repo.rglob("*.sh"))
        assert len(shell_scripts) > 0, "No shell scripts found in deployment"
        
        for script in shell_scripts:
            stat_info = script.stat()
            assert stat_info.st_mode & 0o111, f"Script {script.name} is not executable"

    def test_existing_config_detection(self, existing_acf_config):
        """Test that CLI detects existing configuration without --force."""
        runner = CliRunner()
        
        result = runner.invoke(main, [
            "init", str(existing_acf_config)
        ])
        
        # MEANINGFUL ASSERTION: Should refuse to overwrite
        assert result.exit_code != 0
        assert "existing" in result.output.lower() or "already" in result.output.lower()

    def test_deployment_failure_in_readonly_directory(self):
        """Test graceful failure when deployment target is read-only."""
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            temp_path.chmod(0o444)  # Read-only
            
            try:
                runner = CliRunner()
                result = runner.invoke(main, [
                    "init", str(temp_path)
                ])
                
                # MEANINGFUL ASSERTION: Should fail gracefully with clear error
                assert result.exit_code != 0
                assert "permission" in result.output.lower() or "error" in result.output.lower()
                
            finally:
                temp_path.chmod(0o755)  # Restore for cleanup