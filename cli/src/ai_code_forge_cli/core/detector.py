"""Repository detection utilities."""

import json
import subprocess
from pathlib import Path
from typing import Dict, Optional


class RepositoryDetector:
    """Detects repository metadata using GitHub CLI."""
    
    def __init__(self, repo_path: Path) -> None:
        """Initialize repository detector.
        
        Args:
            repo_path: Path to repository directory
        """
        self.repo_path = repo_path
    
    def detect_github_info(self) -> Dict[str, Optional[str]]:
        """Detect GitHub repository information using gh CLI.
        
        Returns:
            Dictionary with github_owner, project_name, repo_url
        """
        info = {
            "github_owner": None,
            "project_name": None,
            "repo_url": None,
        }
        
        try:
            # Try gh CLI first for accurate GitHub info
            result = subprocess.run(
                ["gh", "repo", "view", "--json", "owner,name,url"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                repo_data = json.loads(result.stdout)
                info["github_owner"] = repo_data.get("owner", {}).get("login")
                info["project_name"] = repo_data["name"]
                info["repo_url"] = repo_data["url"]
                return info
        except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError, FileNotFoundError):
            pass
        
        try:
            # Fallback to git remote origin URL
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                remote_url = result.stdout.strip()
                
                # Parse GitHub URL patterns
                if "github.com" in remote_url:
                    if remote_url.startswith("https://github.com/"):
                        parts = remote_url.replace("https://github.com/", "").rstrip(".git").split("/")
                        if len(parts) >= 2:
                            info["github_owner"] = parts[0]
                            info["project_name"] = parts[1]
                            info["repo_url"] = f"https://github.com/{parts[0]}/{parts[1]}"
                    elif "@github.com:" in remote_url:
                        parts = remote_url.split("@github.com:")[1].rstrip(".git").split("/")
                        if len(parts) >= 2:
                            info["github_owner"] = parts[0]
                            info["project_name"] = parts[1]
                            info["repo_url"] = f"https://github.com/{parts[0]}/{parts[1]}"
        except (subprocess.TimeoutExpired, IndexError, FileNotFoundError):
            pass
        
        # Final fallback to directory name
        if not info["project_name"]:
            info["project_name"] = self.repo_path.name
        
        return info
    
    def is_git_repository(self) -> bool:
        """Check if the path is a git repository.
        
        Returns:
            True if .git directory exists
        """
        return (self.repo_path / ".git").exists()
    
    def check_existing_configuration(self) -> Dict[str, bool]:
        """Check for existing ACF and Claude configuration.
        
        Returns:
            Dictionary with has_acf and has_claude flags
        """
        return {
            "has_acf": (self.repo_path / ".acforge").exists(),
            "has_claude": (self.repo_path / ".claude").exists(),
        }