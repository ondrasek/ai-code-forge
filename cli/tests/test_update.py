"""Tests for acf update command."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime

import pytest
from click.testing import CliRunner

from ai_code_forge_cli.cli import main
from ai_code_forge_cli.core.update import UpdateAnalyzer, CustomizationPreserver, UpdateCommand
from ai_code_forge_cli.core.state import ACFState, InstallationState, TemplateState, FileInfo


class TestUpdateAnalyzer:
    """Test update analysis functionality."""
    
    def test_analyze_not_initialized(self, temp_repo):
        """Test analysis of uninitialized repository."""
        # Mock state and template managers
        state_manager = MagicMock()
        template_manager = MagicMock()
        
        # Mock empty state (not initialized)
        mock_state = ACFState()
        mock_state.installation = None
        state_manager.load_state.return_value = mock_state
        
        analyzer = UpdateAnalyzer(state_manager, template_manager)
        analysis = analyzer.analyze_changes()
        
        assert analysis["status"] == "not_initialized"
        assert not analysis["needs_update"]
    
    def test_analyze_up_to_date(self, temp_repo):
        """Test analysis when templates are up to date."""
        state_manager = MagicMock()
        template_manager = MagicMock()
        
        # Mock initialized state with current checksum
        mock_state = ACFState()
        mock_state.installation = InstallationState(
            cli_version="3.0.0",
            template_version="abc12345",
            installed_at=datetime.now()
        )
        mock_state.templates = TemplateState(checksum="abcdef123456")
        
        state_manager.load_state.return_value = mock_state
        template_manager.calculate_bundle_checksum.return_value = "abcdef123456"
        
        analyzer = UpdateAnalyzer(state_manager, template_manager)
        analysis = analyzer.analyze_changes()
        
        assert analysis["status"] == "up_to_date"
        assert not analysis["needs_update"]
        assert analysis["current_version"] == "abcdef12"
        assert analysis["available_version"] == "abcdef12"
    
    def test_analyze_update_available(self, temp_repo):
        """Test analysis when updates are available."""
        state_manager = MagicMock()
        template_manager = MagicMock()
        
        # Mock initialized state with old checksum
        mock_state = ACFState()
        mock_state.installation = InstallationState(
            cli_version="3.0.0",
            template_version="abc12345",
            installed_at=datetime.now()
        )
        mock_state.templates = TemplateState(
            checksum="old_checksum",
            files={
                "agents/foundation/context.md": FileInfo(
                    checksum="old_file_checksum",
                    size=1024
                ),
                "settings.json": FileInfo(
                    checksum="old_settings_checksum",
                    size=512
                )
            }
        )
        
        state_manager.load_state.return_value = mock_state
        state_manager.repo_root = temp_repo
        
        template_manager.calculate_bundle_checksum.return_value = "new_checksum"
        template_manager.list_template_files.return_value = [
            "agents/foundation/context.md",
            "settings.json", 
            "agents/foundation/patterns.md"  # New template
        ]
        
        def mock_get_template_info(path):
            if path == "agents/foundation/context.md":
                return FileInfo(
                    checksum="new_file_checksum",  # Updated
                    size=1024
                )
            elif path == "settings.json":
                return FileInfo(
                    checksum="old_settings_checksum",  # Unchanged
                    size=512
                )
            elif path == "agents/foundation/patterns.md":
                return FileInfo(
                    checksum="new_pattern_checksum",  # New
                    size=2048
                )
            return None
        
        template_manager.get_template_info.side_effect = mock_get_template_info
        
        analyzer = UpdateAnalyzer(state_manager, template_manager)
        analysis = analyzer.analyze_changes()
        
        assert analysis["status"] == "update_available"
        assert analysis["needs_update"]
        assert analysis["current_version"] == "old_chec"
        assert analysis["available_version"] == "new_chec"
        assert "agents/foundation/patterns.md" in analysis["new_templates"]
        assert "agents/foundation/context.md" in analysis["updated_templates"]
        assert "settings.json" not in analysis["updated_templates"]  # Unchanged
    
    def test_analyze_conflicts(self, temp_repo):
        """Test conflict analysis with local customizations."""
        state_manager = MagicMock()
        template_manager = MagicMock()
        
        state_manager.repo_root = temp_repo
        
        # Create .claude directory with local files
        claude_dir = temp_repo / ".claude"
        claude_dir.mkdir()
        agents_dir = claude_dir / "agents" / "foundation"
        agents_dir.mkdir(parents=True)
        
        # Create .local file with content (potential conflict)
        local_file = agents_dir / "context.local.md"
        local_file.write_text("Custom content")
        
        # Mock state with templates being updated
        mock_state = ACFState()
        mock_state.installation = InstallationState(
            cli_version="3.0.0",
            template_version="abc12345",
            installed_at=datetime.now()
        )
        mock_state.templates = TemplateState(
            checksum="old_checksum",
            files={
                "agents/foundation/context.md": FileInfo(
                    checksum="old_checksum",
                    size=1024
                )
            }
        )
        
        state_manager.load_state.return_value = mock_state
        template_manager.calculate_bundle_checksum.return_value = "new_checksum"
        template_manager.list_template_files.return_value = ["agents/foundation/context.md"]
        template_manager.get_template_info.return_value = FileInfo(
            checksum="new_checksum",
            size=1024
        )
        
        analyzer = UpdateAnalyzer(state_manager, template_manager)
        analysis = analyzer.analyze_changes()
        
        assert analysis["status"] == "update_available"
        assert len(analysis["conflicts"]) > 0
        assert len(analysis["preserved_customizations"]) > 0
        assert any("context.local.md" in conflict for conflict in analysis["conflicts"])


class TestCustomizationPreserver:
    """Test customization preservation functionality."""
    
    def test_identify_customizations(self, temp_repo):
        """Test identification of existing customizations."""
        # Create .claude directory with various customizations
        claude_dir = temp_repo / ".claude"
        claude_dir.mkdir()
        
        # Create .local files
        (claude_dir / "settings.local.json").write_text("{}")
        (claude_dir / "agents" / "custom.local.md").mkdir(parents=True) and \
        (claude_dir / "agents" / "custom.local.md").write_text("# Custom")
        
        # Create custom files
        custom_dir = claude_dir / "custom"
        custom_dir.mkdir()
        (custom_dir / "my_agent.md").write_text("# My Agent")
        
        preserver = CustomizationPreserver(temp_repo)
        customizations = preserver.identify_customizations()
        
        assert len(customizations["local_files"]) == 2
        assert "settings.local.json" in customizations["local_files"]
        assert "agents/custom.local.md" in customizations["local_files"]
        assert len(customizations["custom_files"]) == 1
        assert "custom/my_agent.md" in customizations["custom_files"]
    
    def test_preserve_and_restore(self, temp_repo):
        """Test backup and restore of customizations."""
        # Create .claude directory with customization
        claude_dir = temp_repo / ".claude"
        claude_dir.mkdir()
        local_file = claude_dir / "settings.local.json"
        local_file.write_text('{"custom": true}')
        
        preserver = CustomizationPreserver(temp_repo)
        
        # Create backup
        backups = preserver.preserve_during_update(["settings.local.json"])
        
        assert len(backups) == 1
        assert "settings.local.json" in backups
        backup_path = Path(backups["settings.local.json"])
        assert backup_path.exists()
        assert backup_path.read_text() == '{"custom": true}'
        
        # Simulate file modification during update
        local_file.write_text('{"updated": true}')
        
        # Restore from backup
        restored = preserver.restore_customizations(backups)
        
        assert len(restored) == 1
        assert "settings.local.json" in restored
        assert local_file.read_text() == '{"custom": true}'


class TestUpdateCommand:
    """Test the complete update command functionality."""
    
    def test_update_dry_run(self, temp_repo):
        """Test update command in dry-run mode."""
        update_cmd = UpdateCommand(temp_repo)
        
        with patch.object(update_cmd.analyzer, "analyze_changes") as mock_analyze:
            mock_analyze.return_value = {
                "status": "update_available",
                "needs_update": True,
                "current_version": "old_ver",
                "available_version": "new_ver",
                "new_templates": ["new_template.md"],
                "updated_templates": ["existing_template.md"],
                "removed_templates": [],
                "conflicts": [],
                "preserved_customizations": ["settings.local.json"]
            }
            
            results = update_cmd.run(dry_run=True)
        
        assert results["success"]
        assert "Would update" in results["message"]
        assert len(results["files_preserved"]) == 1
    
    def test_update_not_initialized(self, temp_repo):
        """Test update fails on uninitialized repository."""
        update_cmd = UpdateCommand(temp_repo)
        
        with patch.object(update_cmd.analyzer, "analyze_changes") as mock_analyze:
            mock_analyze.return_value = {
                "status": "not_initialized",
                "needs_update": False
            }
            
            results = update_cmd.run()
        
        assert not results["success"]
        assert "not initialized" in results["errors"][0]
    
    def test_update_up_to_date(self, temp_repo):
        """Test update when already up to date."""
        update_cmd = UpdateCommand(temp_repo)
        
        with patch.object(update_cmd.analyzer, "analyze_changes") as mock_analyze:
            mock_analyze.return_value = {
                "status": "up_to_date",
                "needs_update": False
            }
            
            results = update_cmd.run()
        
        assert results["success"]
        assert "already up to date" in results["message"]
    
    def test_update_conflicts_no_force(self, temp_repo):
        """Test update fails with conflicts when force is not used."""
        update_cmd = UpdateCommand(temp_repo)
        
        with patch.object(update_cmd.analyzer, "analyze_changes") as mock_analyze:
            mock_analyze.return_value = {
                "status": "update_available", 
                "needs_update": True,
                "conflicts": ["settings.local.json"],
                "preserved_customizations": ["settings.local.json"]
            }
            
            results = update_cmd.run(force=False)
        
        assert not results["success"]
        assert "Conflicts detected" in results["errors"][0]
        assert any("Use --force" in warning for warning in results["warnings"])
    
    def test_update_with_force(self, temp_repo):
        """Test update succeeds with force despite conflicts."""
        update_cmd = UpdateCommand(temp_repo)
        
        with patch.object(update_cmd.analyzer, "analyze_changes") as mock_analyze:
            with patch.object(update_cmd, "_perform_update") as mock_perform:
                with patch.object(update_cmd, "_update_state") as mock_update_state:
                    mock_analyze.return_value = {
                        "status": "update_available",
                        "needs_update": True,
                        "available_version": "new_ver",
                        "conflicts": ["settings.local.json"],
                        "preserved_customizations": ["settings.local.json"]
                    }
                    
                    mock_perform.return_value = {
                        "files_updated": ["template.md"],
                        "errors": []
                    }
                    
                    results = update_cmd.run(force=True)
        
        assert results["success"]
        assert mock_perform.called
        assert mock_update_state.called


class TestUpdateCommandCLI:
    """Test the CLI interface for update command."""
    
    def test_update_help(self):
        """Test update command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["update", "--help"])
        
        assert result.exit_code == 0
        assert "Update repository templates" in result.output
        assert "--dry-run" in result.output
        assert "--force" in result.output
    
    def test_update_dry_run_cli(self):
        """Test update command via CLI with dry-run."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            with patch("ai_code_forge_cli.core.update.UpdateCommand.run") as mock_run:
                mock_run.return_value = {
                    "success": True,
                    "message": "Would update 2 templates",
                    "analysis": {
                        "status": "update_available",
                        "current_version": "old123",
                        "available_version": "new456",
                        "new_templates": ["new.md"],
                        "updated_templates": ["existing.md"]
                    },
                    "files_updated": ["template1.md", "template2.md"],
                    "files_preserved": ["settings.local.json"],
                    "warnings": [],
                    "errors": []
                }
                
                result = runner.invoke(main, ["update", "--dry-run"])
        
        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        assert "Update preview" in result.output
    
    def test_update_force_cli(self):
        """Test update command via CLI with force option."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            with patch("ai_code_forge_cli.core.update.UpdateCommand.run") as mock_run:
                mock_run.return_value = {
                    "success": True,
                    "message": "Updated 2 templates",
                    "analysis": {
                        "status": "update_available",
                        "conflicts": ["settings.local.json"]
                    },
                    "files_updated": ["template1.md", "template2.md"],
                    "files_preserved": ["settings.local.json"],
                    "warnings": [],
                    "errors": []
                }
                
                result = runner.invoke(main, ["update", "--force"])
        
        assert result.exit_code == 0
        assert "updated successfully" in result.output.lower()
    
    def test_update_failure_cli(self):
        """Test update command failure via CLI."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            with patch("ai_code_forge_cli.core.update.UpdateCommand.run") as mock_run:
                mock_run.return_value = {
                    "success": False,
                    "message": "Update failed",
                    "analysis": {"status": "not_initialized"},
                    "files_updated": [],
                    "files_preserved": [],
                    "warnings": [],
                    "errors": ["Repository not initialized"]
                }
                
                result = runner.invoke(main, ["update"])
        
        assert result.exit_code == 1
        assert "Update failed" in result.output
        assert "Repository not initialized" in result.output
    
    def test_update_conflicts_cli(self):
        """Test update command with conflicts via CLI."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            with patch("ai_code_forge_cli.core.update.UpdateCommand.run") as mock_run:
                mock_run.return_value = {
                    "success": False,
                    "message": "Conflicts detected",
                    "analysis": {
                        "status": "update_available",
                        "conflicts": ["settings.local.json", "agents/custom.local.md"]
                    },
                    "files_updated": [],
                    "files_preserved": [],
                    "warnings": ["Use --force to proceed"],
                    "errors": ["Conflicts detected. Review conflicts and use --force"]
                }
                
                result = runner.invoke(main, ["update"])
        
        assert result.exit_code == 1
        assert "Customization conflicts detected" in result.output
        assert "settings.local.json" in result.output
        assert "Use --force" in result.output