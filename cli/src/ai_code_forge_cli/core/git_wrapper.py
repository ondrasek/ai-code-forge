"""General git wrapper for ACF command git integration."""

from pathlib import Path
from typing import Dict, Optional, Any

from .git import GitCommitManager, get_current_acf_version


class GitCommandWrapper:
    """General git wrapper that can wrap any ACF command with automatic commits."""
    
    def __init__(self, repository_path: Path, verbose: bool = False):
        """Initialize git wrapper for repository.
        
        Args:
            repository_path: Path to the git repository
            verbose: Enable verbose output
        """
        self.repo_path = repository_path
        self.verbose = verbose
        self.git_manager = GitCommitManager(repository_path)
    
    def should_use_git(self, git_enabled: bool) -> bool:
        """Check if git integration should be used.
        
        Args:
            git_enabled: Whether git flag was provided
            
        Returns:
            True if git integration should proceed
        """
        if not git_enabled:
            return False
        
        if not self.git_manager.is_git_repository():
            if self.verbose:
                print("⚠️  Git integration skipped: Not a git repository")
            return False
        
        return True
    
    def commit_command_changes(
        self, 
        command_name: str, 
        git_enabled: bool,
        old_version: Optional[str] = None,
        new_version: Optional[str] = None,
        custom_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Commit changes made by an ACF command.
        
        Args:
            command_name: Name of the command (e.g., "init", "update", "merge")
            git_enabled: Whether git integration is enabled
            old_version: Previous ACF configuration version (if applicable)
            new_version: New ACF configuration version (if applicable)
            custom_message: Custom commit message (overrides version-based message)
            
        Returns:
            Dictionary with success status and commit info
        """
        result = {"success": False, "error": None, "commit_message": None}
        
        if not self.should_use_git(git_enabled):
            return result
        
        try:
            # Ensure git is configured
            if not self.git_manager.ensure_git_configured():
                result["error"] = "Failed to configure git user settings"
                return result
            
            # Determine commit message
            if custom_message:
                commit_message = custom_message
                display_message = custom_message
            else:
                commit_message, display_message = self._generate_commit_message(
                    command_name, old_version, new_version
                )
            
            # Add ACF-related files
            acf_patterns = self._get_acf_file_patterns()
            
            if not self.git_manager.add_files(acf_patterns):
                result["error"] = "Failed to add files to git"
                return result
            
            # Create commit
            if self.git_manager.commit_changes(commit_message):
                result["success"] = True
                result["commit_message"] = display_message
            else:
                result["error"] = "Failed to create git commit"
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _generate_commit_message(
        self, 
        command_name: str, 
        old_version: Optional[str], 
        new_version: Optional[str]
    ) -> tuple[str, str]:
        """Generate version-based commit message.
        
        Args:
            command_name: Name of the command
            old_version: Previous version
            new_version: New version
            
        Returns:
            Tuple of (full_commit_message, display_message)
        """
        if old_version is None and new_version:
            # Initial deployment
            full_message = f"chore: acforge {command_name} configuration (v{new_version})"
            display_message = f"v{new_version}"
        elif old_version and new_version and old_version != new_version:
            # Version update
            full_message = f"chore: acforge {command_name} configuration ({old_version} → {new_version})"
            display_message = f"{old_version} → {new_version}"
        elif new_version:
            # Same version (re-deployment)
            full_message = f"chore: acforge {command_name} configuration (v{new_version})"
            display_message = f"v{new_version}"
        else:
            # No version info available
            full_message = f"chore: acforge {command_name} configuration update"
            display_message = f"{command_name} update"
        
        return full_message, display_message
    
    def _get_acf_file_patterns(self) -> list[str]:
        """Get list of file patterns to include in git commits.
        
        Returns:
            List of file patterns to add to git
        """
        return [
            ".acforge/",
            ".devcontainer/", 
            "CLAUDE.md"
        ]
    
    def get_current_version(self) -> Optional[str]:
        """Get current ACF version from state if available.
        
        Returns:
            Current version string or None
        """
        acforge_dir = self.repo_path / ".acforge"
        return get_current_acf_version(acforge_dir) if acforge_dir.exists() else None


def create_git_wrapper(ctx_or_path, verbose: bool = False) -> GitCommandWrapper:
    """Create git wrapper from CLI context or path.
    
    Args:
        ctx_or_path: ACFContext object or Path to repository
        verbose: Enable verbose output
        
    Returns:
        GitCommandWrapper instance
    """
    if hasattr(ctx_or_path, 'find_repo_root'):
        # It's an ACFContext
        repo_path = ctx_or_path.find_repo_root()
        verbose = ctx_or_path.verbose or verbose
    else:
        # It's a Path
        repo_path = ctx_or_path
    
    return GitCommandWrapper(repo_path, verbose)