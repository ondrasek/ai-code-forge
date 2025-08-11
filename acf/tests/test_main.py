"""Tests for ACF CLI main module.

Test change to verify git-workflow manual tagging behavior.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from ai_code_forge.main import main, install, status


class TestMainCLI:
    """Test cases for main CLI functionality."""
    
    def setup_method(self):
        """Setup test runner."""
        self.runner = CliRunner()
    
    def test_main_group_help(self):
        """Test main command shows help."""
        result = self.runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "AI Code Forge configuration management tool" in result.output
    
    def test_main_version(self):
        """Test version option works."""
        result = self.runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.2.0" in result.output
    
    def test_install_command_help(self):
        """Test install command help."""
        result = self.runner.invoke(main, ["install", "--help"])
        assert result.exit_code == 0
        assert "--target" in result.output
        assert "--force" in result.output
    
    def test_status_command_help(self):
        """Test status command help."""
        result = self.runner.invoke(main, ["status", "--help"])
        assert result.exit_code == 0
        assert "--target" in result.output
    
    def test_install_nonexistent_target(self):
        """Test install with nonexistent target directory."""
        result = self.runner.invoke(main, ["install", "--target", "/nonexistent/path"])
        assert result.exit_code == 0
        assert "Target directory does not exist" in result.output
    
    @patch('ai_code_forge.main.ACFInstaller')
    def test_install_already_exists(self, mock_installer_class):
        """Test install when configuration already exists."""
        # Mock installer
        mock_installer = MagicMock()
        mock_installer.get_installation_status.return_value = {
            "claude_dir_exists": True,
            "acf_dir_exists": False
        }
        mock_installer_class.return_value = mock_installer
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(main, ["install"])
            assert result.exit_code == 0
            assert "already exists" in result.output
            assert "--force" in result.output
    
    @patch('ai_code_forge.main.ACFInstaller')
    def test_install_success(self, mock_installer_class):
        """Test successful install."""
        # Mock installer
        mock_installer = MagicMock()
        mock_installer.get_installation_status.return_value = {
            "claude_dir_exists": False,
            "acf_dir_exists": False
        }
        mock_installer.install.return_value = True
        mock_installer_class.return_value = mock_installer
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(main, ["install"])
            assert result.exit_code == 0
            assert "Ready to use!" in result.output
            mock_installer.install.assert_called_once()
    
    @patch('ai_code_forge.main.ACFInstaller')
    def test_install_force(self, mock_installer_class):
        """Test force install."""
        # Mock installer
        mock_installer = MagicMock()
        mock_installer.get_installation_status.return_value = {
            "claude_dir_exists": True,
            "acf_dir_exists": True
        }
        mock_installer.install.return_value = True
        mock_installer_class.return_value = mock_installer
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(main, ["install", "--force"])
            assert result.exit_code == 0
            assert "Force installation" in result.output
            mock_installer.install.assert_called_once()
    
    @patch('ai_code_forge.main.ACFInstaller')
    def test_install_failure(self, mock_installer_class):
        """Test install failure."""
        # Mock installer
        mock_installer = MagicMock()
        mock_installer.get_installation_status.return_value = {
            "claude_dir_exists": False,
            "acf_dir_exists": False
        }
        mock_installer.install.return_value = False
        mock_installer_class.return_value = mock_installer
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(main, ["install"])
            assert result.exit_code == 0
            # Should not show success message when install fails
            assert "Ready to use!" not in result.output
    
    @patch('ai_code_forge.main.ACFInstaller')
    def test_status_complete_installation(self, mock_installer_class):
        """Test status with complete installation."""
        # Mock installer
        mock_installer = MagicMock()
        mock_installer.get_installation_status.return_value = {
            "claude_dir_exists": True,
            "acf_dir_exists": True,
            "claude_md_exists": True,
            "claude_files": ["agents", "commands", "settings.json"],
            "acf_files": ["README.md", "CHANGELOG.md", "templates"]
        }
        mock_installer_class.return_value = mock_installer
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(main, ["status"])
            assert result.exit_code == 0
            assert "Complete ACF installation detected!" in result.output
            assert "agents" in result.output
            assert "README.md" in result.output
    
    @patch('ai_code_forge.main.ACFInstaller')
    def test_status_no_installation(self, mock_installer_class):
        """Test status with no installation."""
        # Mock installer
        mock_installer = MagicMock()
        mock_installer.get_installation_status.return_value = {
            "claude_dir_exists": False,
            "acf_dir_exists": False,
            "claude_md_exists": False,
            "claude_files": [],
            "acf_files": []
        }
        mock_installer_class.return_value = mock_installer
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(main, ["status"])
            assert result.exit_code == 0
            assert "No ACF installation found" in result.output
            assert "run 'ai-code-forge install'" in result.output
    
    @patch('ai_code_forge.main.ACFInstaller')
    def test_status_partial_installation(self, mock_installer_class):
        """Test status with partial installation."""
        # Mock installer
        mock_installer = MagicMock()
        mock_installer.get_installation_status.return_value = {
            "claude_dir_exists": True,
            "acf_dir_exists": False,
            "claude_md_exists": False,
            "claude_files": ["settings.json"],
            "acf_files": []
        }
        mock_installer_class.return_value = mock_installer
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(main, ["status"])
            assert result.exit_code == 0
            assert "Partial ACF installation" in result.output
            assert "run 'ai-code-forge install' to complete" in result.output
    
    def test_status_with_target_directory(self):
        """Test status command with target directory."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(main, ["status", "--target", "."])
            assert result.exit_code == 0
            assert "Installation Status for:" in result.output