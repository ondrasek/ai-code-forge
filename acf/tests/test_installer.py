"""Tests for ACF installer functionality."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from ai_code_forge.core.installer import ACFInstaller


class TestACFInstaller:
    """Test cases for ACFInstaller class."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.installer = ACFInstaller(self.temp_dir)
        
    def teardown_method(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_installer_initialization(self):
        """Test installer initializes correctly."""
        assert self.installer.target_dir == self.temp_dir
        assert self.installer.claude_dir == self.temp_dir / ".claude"
        assert self.installer.acf_dir == self.temp_dir / ".acf"
    
    def test_installer_default_target_dir(self):
        """Test installer uses current directory by default."""
        installer = ACFInstaller()
        assert installer.target_dir == Path.cwd()
    
    def test_get_installation_status_empty(self):
        """Test status of empty directory."""
        status = self.installer.get_installation_status()
        
        assert not status["claude_dir_exists"]
        assert not status["acf_dir_exists"]
        assert not status["claude_md_exists"]
        assert status["claude_files"] == []
        assert status["acf_files"] == []
    
    def test_get_installation_status_with_files(self):
        """Test status with installed files."""
        # Create directories and files
        self.installer.claude_dir.mkdir()
        self.installer.acf_dir.mkdir()
        (self.installer.claude_dir / "settings.json").write_text('{}')
        (self.installer.acf_dir / "README.md").write_text('# Test')
        (self.temp_dir / "CLAUDE.md").write_text('# Rules')
        
        status = self.installer.get_installation_status()
        
        assert status["claude_dir_exists"]
        assert status["acf_dir_exists"] 
        assert status["claude_md_exists"]
        assert "settings.json" in status["claude_files"]
        assert "README.md" in status["acf_files"]
    
    @patch.object(ACFInstaller, 'get_package_data_path')
    def test_install_success(self, mock_get_path):
        """Test successful installation."""
        # Mock package data directory
        mock_data_dir = Path(tempfile.mkdtemp())
        mock_get_path.return_value = mock_data_dir
        
        # Create mock package data structure
        claude_dir = mock_data_dir / "claude"
        acf_dir = mock_data_dir / "acf"
        claude_dir.mkdir(parents=True)
        acf_dir.mkdir(parents=True)
        
        (claude_dir / "settings.json").write_text('{"test": "data"}')
        (acf_dir / "README.md").write_text('# ACF Tool')
        (mock_data_dir / "CLAUDE.md").write_text('# Operational Rules')
        
        # Test installation
        result = self.installer.install()
        
        assert result is True
        assert self.installer.claude_dir.exists()
        assert self.installer.acf_dir.exists()
        assert (self.installer.claude_dir / "settings.json").exists()
        assert (self.installer.acf_dir / "README.md").exists()
        assert (self.temp_dir / "CLAUDE.md").exists()
        
        # Cleanup
        shutil.rmtree(mock_data_dir)
    
    @patch.object(ACFInstaller, 'get_package_data_path')
    def test_install_missing_source_data(self, mock_get_path):
        """Test installation with missing source data."""
        # Mock non-existent data directory
        mock_data_dir = Path(tempfile.mkdtemp())
        mock_get_path.return_value = mock_data_dir
        
        # Don't create any source files
        
        result = self.installer.install()
        
        assert result is False
        
        # Cleanup
        shutil.rmtree(mock_data_dir)
    
    def test_create_directories(self):
        """Test directory creation."""
        assert not self.installer.claude_dir.exists()
        assert not self.installer.acf_dir.exists()
        
        self.installer._create_directories()
        
        assert self.installer.claude_dir.exists()
        assert self.installer.acf_dir.exists()
    
    @patch.object(ACFInstaller, 'get_package_data_path')
    def test_install_claude_files(self, mock_get_path):
        """Test Claude Code files installation."""
        # Setup mock data
        mock_data_dir = Path(tempfile.mkdtemp())
        mock_get_path.return_value = mock_data_dir
        
        claude_dir = mock_data_dir / "claude"
        claude_dir.mkdir(parents=True)
        (claude_dir / "settings.json").write_text('{}')
        
        agents_dir = claude_dir / "agents"
        agents_dir.mkdir()
        (agents_dir / "test-agent.md").write_text('# Test Agent')
        
        # Create target directory
        self.installer.claude_dir.mkdir()
        
        # Test installation
        self.installer._install_claude_files(mock_data_dir)
        
        assert (self.installer.claude_dir / "settings.json").exists()
        assert (self.installer.claude_dir / "agents" / "test-agent.md").exists()
        
        # Cleanup
        shutil.rmtree(mock_data_dir)
    
    @patch.object(ACFInstaller, 'get_package_data_path')  
    def test_install_acf_files(self, mock_get_path):
        """Test ACF files installation."""
        # Setup mock data
        mock_data_dir = Path(tempfile.mkdtemp())
        mock_get_path.return_value = mock_data_dir
        
        acf_dir = mock_data_dir / "acf"
        acf_dir.mkdir(parents=True)
        (acf_dir / "README.md").write_text('# ACF Tool')
        (acf_dir / "CHANGELOG.md").write_text('# Changes')
        
        templates_dir = acf_dir / "templates"
        templates_dir.mkdir()
        (templates_dir / "test-template.md").write_text('# Template')
        
        # Create target directory
        self.installer.acf_dir.mkdir()
        
        # Test installation
        self.installer._install_acf_files(mock_data_dir)
        
        assert (self.installer.acf_dir / "README.md").exists()
        assert (self.installer.acf_dir / "CHANGELOG.md").exists()
        assert (self.installer.acf_dir / "templates" / "test-template.md").exists()
        
        # Cleanup
        shutil.rmtree(mock_data_dir)
    
    @patch.object(ACFInstaller, 'get_package_data_path')
    def test_install_claude_md(self, mock_get_path):
        """Test CLAUDE.md installation."""
        # Setup mock data
        mock_data_dir = Path(tempfile.mkdtemp())
        mock_get_path.return_value = mock_data_dir
        
        (mock_data_dir / "CLAUDE.md").write_text('# Operational Rules')
        
        # Test installation
        self.installer._install_claude_md(mock_data_dir)
        
        claude_md_path = self.temp_dir / "CLAUDE.md"
        assert claude_md_path.exists()
        assert claude_md_path.read_text() == '# Operational Rules'
        
        # Cleanup
        shutil.rmtree(mock_data_dir)
    
    def test_get_package_data_path_development(self):
        """Test package data path detection in development."""
        # This test will use the actual development path
        path = self.installer.get_package_data_path()
        assert path.exists()
        assert (path / "claude").exists() or "Package data" in str(path)
    
    @patch('ai_code_forge.core.installer.resources.files')
    def test_get_package_data_path_installed_package(self, mock_resources):
        """Test package data path for installed package."""
        # Mock the case where development path doesn't exist
        installer = ACFInstaller()
        
        # Mock a non-existent development path
        with patch.object(Path, 'exists', return_value=False):
            mock_traversable = MagicMock()
            mock_traversable.__fspath__ = MagicMock(return_value="/mock/path")
            mock_resources.return_value = mock_traversable
            
            path = installer.get_package_data_path()
            assert str(path) == "/mock/path"