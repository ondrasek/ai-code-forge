"""Git integration utilities for ACF deployment."""

import subprocess
from pathlib import Path
from typing import Any, Optional


class GitCommitManager:
    """Manages git commits for ACF deployment operations."""
    
    def __init__(self, repository_path: Path):
        """Initialize git manager for repository.
        
        Args:
            repository_path: Path to the git repository
        """
        self.repo_path = repository_path
    
    def is_git_repository(self) -> bool:
        """Check if the current directory is a git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def is_working_directory_clean(self) -> bool:
        """Check if working directory has no uncommitted changes."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            return result.returncode == 0 and not result.stdout.strip()
        except subprocess.CalledProcessError:
            return False
    
    def add_files(self, file_patterns: list[str]) -> bool:
        """Add files to git staging area.
        
        Args:
            file_patterns: List of file patterns to add (e.g., [".acforge/", "CLAUDE.md"])
            
        Returns:
            True if successful
        """
        try:
            for pattern in file_patterns:
                result = subprocess.run(
                    ["git", "add", pattern],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    return False
            return True
        except subprocess.CalledProcessError:
            return False
    
    def commit_changes(self, commit_message: str) -> bool:
        """Commit staged changes with message.
        
        Args:
            commit_message: Git commit message
            
        Returns:
            True if successful
        """
        try:
            result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False
    
    def create_acf_deployment_commit(
        self, 
        old_version: Optional[str], 
        new_version: str,
        operation: str = "initialize"
    ) -> bool:
        """Create a commit for ACF deployment with version-based message.
        
        Args:
            old_version: Previous ACF configuration version (None for initial deployment)
            new_version: New ACF configuration version
            operation: Type of operation ("initialize", "update", "merge")
            
        Returns:
            True if successful
        """
        # Add all ACF-related files
        acf_patterns = [".acforge/", ".devcontainer/", "CLAUDE.md"]
        
        if not self.add_files(acf_patterns):
            return False
        
        # Generate version-based commit message
        if old_version is None:
            commit_message = f"chore: acforge {operation} configuration (v{new_version})"
        else:
            commit_message = f"chore: acforge {operation} configuration ({old_version} → {new_version})"
        
        return self.commit_changes(commit_message)
    
    def ensure_git_configured(self) -> bool:
        """Check if we're in a git repository - do not modify git configuration.
        
        Returns:
            True if in a git repository, False otherwise
        """
        # Only check if we're in a git repository - never modify configuration
        return self.is_git_repository()
    
    def get_repo_status(self) -> dict[str, Any]:
        """Get git repository status.
        
        Returns:
            Dictionary with success status and repo information
        """
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return {
                    "success": True,
                    "has_changes": bool(result.stdout.strip()),
                    "status_output": result.stdout.strip()
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr.strip() or "Git status failed"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


def get_current_acf_version(acforge_dir: Path) -> Optional[str]:
    """Get current ACF version from state.json if it exists.
    
    Args:
        acforge_dir: Path to .acforge directory
        
    Returns:
        Current version string or None if not found
    """
    import json
    
    state_file = acforge_dir / "state.json"
    if not state_file.exists():
        return None
    
    try:
        with open(state_file) as f:
            state_data = json.load(f)
        return state_data.get("installation", {}).get("template_version")
    except (json.JSONDecodeError, KeyError):
        return None