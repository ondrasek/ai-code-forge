"""Integration tests for ACF CLI."""

import pytest
import tempfile
import os
from pathlib import Path
from click.testing import CliRunner

from ai_code_forge.main import main


class TestCLIIntegration:
    """Integration tests for full CLI workflow."""
    
    def setup_method(self):
        """Setup test environment."""
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_install_in_isolated_directory(self):
        """Test install command in isolated directory."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(main, ["install"])
            assert result.exit_code == 0
            assert "🚀 Installing ACF configuration to:" in result.output
    
    def test_status_after_install(self):
        """Test status command after install."""
        with self.runner.isolated_filesystem():
            # First install
            install_result = self.runner.invoke(main, ["install"])
            assert install_result.exit_code == 0
            
            # Then check status
            status_result = self.runner.invoke(main, ["status"])
            assert status_result.exit_code == 0
            assert "📊 ACF Installation Status for:" in status_result.output
    
    def test_command_order_independence(self):
        """Test commands work in any order."""
        with self.runner.isolated_filesystem():
            # Status before install should work
            result1 = self.runner.invoke(main, ["status"])
            assert result1.exit_code == 0
            
            # Install should work
            result2 = self.runner.invoke(main, ["install"])
            assert result2.exit_code == 0
            
            # Status after install should work
            result3 = self.runner.invoke(main, ["status"])
            assert result3.exit_code == 0
    
    @pytest.mark.parametrize("command", ["install", "status"])
    def test_commands_handle_missing_directories(self, command):
        """Test commands handle missing directories gracefully."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(main, [command])
            # Should not crash, even if directories don't exist
            assert result.exit_code == 0