"""Tests for acf init command."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from ai_code_forge_cli.cli import main
from ai_code_forge_cli.core.detector import RepositoryDetector
from ai_code_forge_cli.core.deployer import ParameterSubstitutor
from ai_code_forge_cli.commands.init import _run_init


class TestParameterSubstitutor:
    """Test parameter substitution functionality."""
    
    def test_basic_substitution(self):
        """Test basic parameter substitution."""
        parameters = {
            "GITHUB_OWNER": "testowner",
            "PROJECT_NAME": "testproject",
        }
        
        substitutor = ParameterSubstitutor(parameters)
        content = "Owner: {{GITHUB_OWNER}}, Project: {{PROJECT_NAME}}"
        
        result = substitutor.substitute_content(content)
        
        assert result == "Owner: testowner, Project: testproject"
        assert set(substitutor.get_substituted_parameters()) == {"GITHUB_OWNER", "PROJECT_NAME"}
    
    def test_missing_parameters(self):
        """Test handling of missing parameters."""
        parameters = {"GITHUB_OWNER": "testowner"}
        
        substitutor = ParameterSubstitutor(parameters)
        content = "Owner: {{GITHUB_OWNER}}, Project: {{PROJECT_NAME}}"
        
        result = substitutor.substitute_content(content)
        
        assert result == "Owner: testowner, Project: {{PROJECT_NAME}}"
        assert substitutor.get_substituted_parameters() == ["GITHUB_OWNER"]
    
    def test_no_parameters(self):
        """Test content with no parameters."""
        parameters = {"GITHUB_OWNER": "testowner"}
        
        substitutor = ParameterSubstitutor(parameters)
        content = "This is plain content"
        
        result = substitutor.substitute_content(content)
        
        assert result == "This is plain content"
        assert substitutor.get_substituted_parameters() == []
    
    def test_multiple_occurrences(self):
        """Test multiple occurrences of same parameter."""
        parameters = {"NAME": "test"}
        
        substitutor = ParameterSubstitutor(parameters)
        content = "{{NAME}} and {{NAME}} again"
        
        result = substitutor.substitute_content(content)
        
        assert result == "test and test again"
        assert substitutor.get_substituted_parameters() == ["NAME"]


class TestRepositoryDetector:
    """Test repository detection functionality."""
    
    def test_github_info_detection_gh_success(self):
        """Test GitHub info detection with successful gh CLI."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            detector = RepositoryDetector(repo_path)
            
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = json.dumps({
                "owner": {"login": "testowner"},
                "name": "testproject", 
                "url": "https://github.com/testowner/testproject"
            })
            
            with patch("subprocess.run", return_value=mock_result):
                info = detector.detect_github_info()
            
            assert info["github_owner"] == "testowner"
            assert info["project_name"] == "testproject"
            assert info["repo_url"] == "https://github.com/testowner/testproject"
    
    def test_github_info_detection_git_fallback(self):
        """Test fallback to git remote when gh CLI fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            detector = RepositoryDetector(repo_path)
            
            def mock_run(*args, **kwargs):
                if "gh" in args[0]:
                    # gh CLI fails
                    mock_result = MagicMock()
                    mock_result.returncode = 1
                    return mock_result
                elif "git" in args[0]:
                    # git remote succeeds
                    mock_result = MagicMock()
                    mock_result.returncode = 0
                    mock_result.stdout = "https://github.com/gitowner/gitproject.git"
                    return mock_result
            
            with patch("subprocess.run", side_effect=mock_run):
                info = detector.detect_github_info()
            
            assert info["github_owner"] == "gitowner"
            assert info["project_name"] == "gitproject"
            assert info["repo_url"] == "https://github.com/gitowner/gitproject"
    
    def test_directory_name_fallback(self):
        """Test fallback to directory name."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "myproject"
            repo_path.mkdir()
            detector = RepositoryDetector(repo_path)
            
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = Exception("Command failed")
                info = detector.detect_github_info()
            
            assert info["github_owner"] is None
            assert info["project_name"] == "myproject"
            assert info["repo_url"] is None
    
    def test_is_git_repository(self):
        """Test git repository detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            detector = RepositoryDetector(repo_path)
            
            # Not a git repo initially
            assert not detector.is_git_repository()
            
            # Create .git directory
            (repo_path / ".git").mkdir()
            assert detector.is_git_repository()
    
    def test_check_existing_configuration(self):
        """Test existing configuration detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            detector = RepositoryDetector(repo_path)
            
            # No existing config
            config = detector.check_existing_configuration()
            assert not config["has_acf"]
            assert not config["has_claude"]
            
            # Create .acf directory
            (repo_path / ".acf").mkdir()
            config = detector.check_existing_configuration()
            assert config["has_acf"]
            assert not config["has_claude"]
            
            # Create .claude directory
            (repo_path / ".claude").mkdir()
            config = detector.check_existing_configuration()
            assert config["has_acf"]
            assert config["has_claude"]


class TestInitCommand:
    """Test the complete init command functionality."""
    
    def test_init_dry_run(self):
        """Test init command in dry-run mode."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            init_cmd = InitCommand(repo_path)
            
            with patch.object(init_cmd.template_manager, "list_template_files") as mock_list:
                with patch.object(init_cmd.template_manager, "get_template_content") as mock_content:
                    mock_list.return_value = ["agents/foundation/context.md", "settings.json"]
                    mock_content.return_value = "Test content with {{PROJECT_NAME}}"
                    
                    results = init_cmd.run(dry_run=True, project_name="testproject")
            
            assert results["success"]
            assert ".acf/" in results["files_created"]
            assert len([f for f in results["files_created"] if not f.endswith("/")]) > 0
            
            # Verify no actual files were created
            assert not (repo_path / ".acf").exists()
            assert not (repo_path / ".claude").exists()
    
    def test_init_existing_config_no_force(self):
        """Test init fails on existing configuration without force."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / ".claude").mkdir()  # Create existing config
            
            init_cmd = InitCommand(repo_path)
            results = init_cmd.run(force=False)
            
            assert not results["success"]
            assert "already exists" in results["errors"][0]
    
    def test_init_existing_config_with_force(self):
        """Test init succeeds on existing configuration with force."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            (repo_path / ".claude").mkdir()  # Create existing config
            
            init_cmd = InitCommand(repo_path)
            
            with patch.object(init_cmd.template_manager, "list_template_files") as mock_list:
                with patch.object(init_cmd.template_manager, "get_template_content") as mock_content:
                    with patch.object(init_cmd.template_manager, "calculate_bundle_checksum") as mock_checksum:
                        mock_list.return_value = ["settings.json"]
                        mock_content.return_value = "{}"
                        mock_checksum.return_value = "abc123"
                        
                        results = init_cmd.run(force=True, project_name="testproject")
            
            assert results["success"]
    
    def test_init_nonexistent_directory(self):
        """Test init fails on nonexistent directory."""
        nonexistent_path = Path("/nonexistent/directory")
        init_cmd = InitCommand(nonexistent_path)
        
        results = init_cmd.run()
        
        assert not results["success"]
        assert "does not exist" in results["errors"][0]


class TestInitCommandCLI:
    """Test the CLI interface for init command."""
    
    def test_init_help(self):
        """Test init command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["init", "--help"])
        
        assert result.exit_code == 0
        assert "Initialize repository" in result.output
        assert "--force" in result.output
        assert "--dry-run" in result.output
    
    def test_init_dry_run_cli(self):
        """Test init command via CLI with dry-run."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            with patch("ai_code_forge_cli.core.init.InitCommand.run") as mock_run:
                mock_run.return_value = {
                    "success": True,
                    "message": "Test success",
                    "files_created": [".acf/", ".claude/settings.json"],
                    "parameters_used": {"PROJECT_NAME": "test"},
                    "warnings": [],
                    "errors": [],
                }
                
                result = runner.invoke(main, ["init", "--dry-run"])
        
        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        assert "preview" in result.output
    
    def test_init_force_cli(self):
        """Test init command via CLI with force option."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            with patch("ai_code_forge_cli.core.init.InitCommand.run") as mock_run:
                mock_run.return_value = {
                    "success": True,
                    "message": "Test success",
                    "files_created": [".acf/", ".claude/settings.json"],
                    "parameters_used": {"PROJECT_NAME": "test"},
                    "warnings": [],
                    "errors": [],
                }
                
                result = runner.invoke(main, ["init", "--force"])
        
        assert result.exit_code == 0
        assert "initialization complete" in result.output.lower()
    
    def test_init_failure_cli(self):
        """Test init command failure via CLI."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            with patch("ai_code_forge_cli.core.init.InitCommand.run") as mock_run:
                mock_run.return_value = {
                    "success": False,
                    "message": "Test failure", 
                    "files_created": [],
                    "parameters_used": {},
                    "warnings": [],
                    "errors": ["Test error message"],
                }
                
                result = runner.invoke(main, ["init"])
        
        assert result.exit_code == 1
        assert "failed" in result.output.lower()
        assert "Test error message" in result.output