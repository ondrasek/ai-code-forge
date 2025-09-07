"""Unit tests for GitCommandWrapper functionality."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from ai_code_forge_cli.core.git_wrapper import GitCommandWrapper, create_git_wrapper
from ai_code_forge_cli.cli import ACFContext


class TestGitCommandWrapper:
    """Test GitCommandWrapper methods in isolation."""
    
    def test_initialization(self, temp_repo):
        """Test wrapper initializes correctly."""
        wrapper = GitCommandWrapper(temp_repo, verbose=False)
        assert wrapper.repo_path == temp_repo
        assert wrapper.verbose is False
        assert wrapper.git_manager is not None
    
    def test_should_use_git_disabled(self, temp_repo):
        """Test git integration disabled when flag is False."""
        wrapper = GitCommandWrapper(temp_repo)
        result = wrapper.should_use_git(git_enabled=False)
        assert result is False
    
    @patch('ai_code_forge_cli.core.git_wrapper.GitCommitManager')
    def test_should_use_git_not_repository(self, mock_git_manager, temp_repo):
        """Test git integration disabled when not a git repository."""
        mock_git_manager.return_value.is_git_repository.return_value = False
        
        wrapper = GitCommandWrapper(temp_repo, verbose=True)
        result = wrapper.should_use_git(git_enabled=True)
        
        assert result is False
    
    @patch('ai_code_forge_cli.core.git_wrapper.GitCommitManager')
    def test_should_use_git_enabled_and_repository(self, mock_git_manager, temp_repo):
        """Test git integration enabled when flag is True and in git repo."""
        mock_git_manager.return_value.is_git_repository.return_value = True
        
        wrapper = GitCommandWrapper(temp_repo)
        result = wrapper.should_use_git(git_enabled=True)
        
        assert result is True
    
    def test_generate_commit_message_initial(self, temp_repo):
        """Test commit message generation for initial deployment."""
        wrapper = GitCommandWrapper(temp_repo)
        
        full_msg, display_msg = wrapper._generate_commit_message(
            command_name="init",
            old_version=None,
            new_version="abc12345"
        )
        
        assert full_msg == "chore: acforge init configuration (vabc12345)"
        assert display_msg == "vabc12345"
    
    def test_generate_commit_message_update(self, temp_repo):
        """Test commit message generation for version update."""
        wrapper = GitCommandWrapper(temp_repo)
        
        full_msg, display_msg = wrapper._generate_commit_message(
            command_name="update",
            old_version="abc12345",
            new_version="def67890"
        )
        
        assert full_msg == "chore: acforge update configuration (abc12345 → def67890)"
        assert display_msg == "abc12345 → def67890"
    
    def test_generate_commit_message_same_version(self, temp_repo):
        """Test commit message generation for same version deployment."""
        wrapper = GitCommandWrapper(temp_repo)
        
        full_msg, display_msg = wrapper._generate_commit_message(
            command_name="update",
            old_version="abc12345",
            new_version="abc12345"
        )
        
        assert full_msg == "chore: acforge update configuration (vabc12345)"
        assert display_msg == "vabc12345"
    
    def test_generate_commit_message_no_versions(self, temp_repo):
        """Test commit message generation with no version information."""
        wrapper = GitCommandWrapper(temp_repo)
        
        full_msg, display_msg = wrapper._generate_commit_message(
            command_name="sync",
            old_version=None,
            new_version=None
        )
        
        assert full_msg == "chore: acforge sync configuration update"
        assert display_msg == "sync update"
    
    def test_acf_file_patterns(self, temp_repo):
        """Test ACF file patterns for git add operations."""
        wrapper = GitCommandWrapper(temp_repo)
        patterns = wrapper._get_acf_file_patterns()
        
        expected_patterns = [".acforge/", ".claude/", ".devcontainer/", "CLAUDE.md"]
        assert patterns == expected_patterns
    
    @patch('ai_code_forge_cli.core.git_wrapper.get_current_acf_version')
    def test_get_current_version_with_state(self, mock_get_version, temp_repo):
        """Test getting current version from state file."""
        mock_get_version.return_value = "test-version"
        
        # Create .acforge directory
        acforge_dir = temp_repo / ".acforge"
        acforge_dir.mkdir()
        
        wrapper = GitCommandWrapper(temp_repo)
        version = wrapper.get_current_version()
        
        assert version == "test-version"
        mock_get_version.assert_called_once_with(acforge_dir)
    
    def test_get_current_version_no_state(self, temp_repo):
        """Test getting current version when no state exists."""
        wrapper = GitCommandWrapper(temp_repo)
        version = wrapper.get_current_version()
        
        assert version is None


class TestCreateGitWrapper:
    """Test git wrapper factory function."""
    
    def test_create_from_context(self, temp_repo):
        """Test creating wrapper from ACFContext."""
        ctx = ACFContext()
        ctx.repo_root = temp_repo
        ctx.verbose = True
        
        with patch.object(ctx, 'find_repo_root', return_value=temp_repo):
            wrapper = create_git_wrapper(ctx, verbose=False)
        
        assert isinstance(wrapper, GitCommandWrapper)
        assert wrapper.repo_path == temp_repo
        assert wrapper.verbose is True  # Context verbose takes precedence
    
    def test_create_from_path(self, temp_repo):
        """Test creating wrapper from Path object."""
        wrapper = create_git_wrapper(temp_repo, verbose=True)
        
        assert isinstance(wrapper, GitCommandWrapper)
        assert wrapper.repo_path == temp_repo
        assert wrapper.verbose is True


class TestGitIntegrationErrors:
    """Test error scenarios in git integration."""
    
    @patch('ai_code_forge_cli.core.git_wrapper.GitCommitManager')
    def test_commit_changes_git_not_configured(self, mock_git_manager, temp_repo):
        """Test handling git configuration failure."""
        mock_manager = mock_git_manager.return_value
        mock_manager.is_git_repository.return_value = True
        mock_manager.ensure_git_configured.return_value = False
        
        wrapper = GitCommandWrapper(temp_repo)
        result = wrapper.commit_command_changes(
            command_name="test",
            git_enabled=True
        )
        
        assert result["success"] is False
        assert "Not a git repository or git not available" in result["error"]
    
    @patch('ai_code_forge_cli.core.git_wrapper.GitCommitManager')
    def test_commit_changes_add_files_failure(self, mock_git_manager, temp_repo):
        """Test handling git add failure."""
        mock_manager = mock_git_manager.return_value
        mock_manager.is_git_repository.return_value = True
        mock_manager.ensure_git_configured.return_value = True
        mock_manager.add_files.return_value = False
        
        wrapper = GitCommandWrapper(temp_repo)
        result = wrapper.commit_command_changes(
            command_name="test",
            git_enabled=True
        )
        
        assert result["success"] is False
        assert "Failed to add files to git" in result["error"]
    
    @patch('ai_code_forge_cli.core.git_wrapper.GitCommitManager')
    def test_commit_changes_commit_failure(self, mock_git_manager, temp_repo):
        """Test handling git commit failure."""
        mock_manager = mock_git_manager.return_value
        mock_manager.is_git_repository.return_value = True
        mock_manager.ensure_git_configured.return_value = True
        mock_manager.add_files.return_value = True
        mock_manager.commit_changes.return_value = False
        
        wrapper = GitCommandWrapper(temp_repo)
        result = wrapper.commit_command_changes(
            command_name="test",
            git_enabled=True
        )
        
        assert result["success"] is False
        assert "Failed to create git commit" in result["error"]
    
    @patch('ai_code_forge_cli.core.git_wrapper.GitCommitManager')
    def test_commit_changes_exception(self, mock_git_manager, temp_repo):
        """Test handling unexpected exceptions."""
        mock_manager = mock_git_manager.return_value
        mock_manager.is_git_repository.side_effect = Exception("Test exception")
        
        wrapper = GitCommandWrapper(temp_repo)
        result = wrapper.commit_command_changes(
            command_name="test",
            git_enabled=True
        )
        
        # Should skip git integration gracefully (no exception propagated)
        assert result["success"] is False
        assert result["error"] is None  # No error, just skipped