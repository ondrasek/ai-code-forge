"""Test utilities for CLI testing."""

import tempfile
from pathlib import Path
from typing import Dict, List, Set


class DeploymentValidator:
    """Utility class for validating CLI deployment results."""
    
    def __init__(self, deployment_path: Path):
        self.deployment_path = deployment_path
    
    def validate_directory_structure(self) -> List[str]:
        """Validate expected directory structure exists. Returns list of errors."""
        errors = []
        
        expected_dirs = [
            ".acforge",
            ".acforge/guidelines", 
            ".acforge/scripts",
            ".acforge/mcp-servers",
            ".acforge/prompts",
            ".acforge/stacks",
            ".acforge/readme",
            ".devcontainer",
            ".devcontainer/postCreate-scripts"
        ]
        
        for dir_path in expected_dirs:
            full_path = self.deployment_path / dir_path
            if not full_path.is_dir():
                errors.append(f"Missing directory: {dir_path}")
        
        return errors
    
    def validate_critical_files(self) -> List[str]:
        """Validate critical files exist. Returns list of errors."""
        errors = []
        
        critical_files = [
            "CLAUDE.md",
            ".acforge/state.json",
            ".acforge/guidelines/CLAUDE.md",
            ".acforge/scripts/launch-claude.sh",
            ".acforge/mcp-servers/mcp-config.json",
            ".devcontainer/devcontainer.json",
            ".devcontainer/postCreate.sh"
        ]
        
        for file_path in critical_files:
            full_path = self.deployment_path / file_path
            if not full_path.is_file():
                errors.append(f"Missing critical file: {file_path}")
        
        return errors
    
    def validate_file_counts(self) -> Dict[str, int]:
        """Return file counts for each major directory."""
        counts = {}
        
        # Count files in major directories
        if (self.deployment_path / ".acforge").exists():
            counts["acforge_total"] = len(list((self.deployment_path / ".acforge").rglob("*")))
            counts["acforge_files"] = len([f for f in (self.deployment_path / ".acforge").rglob("*") if f.is_file()])
        
        if (self.deployment_path / ".devcontainer").exists():
            counts["devcontainer_files"] = len([f for f in (self.deployment_path / ".devcontainer").rglob("*") if f.is_file()])
        
        # Count root files
        counts["root_files"] = len([f for f in self.deployment_path.iterdir() if f.is_file()])
        
        return counts
    
    def validate_parameter_substitution(self, expected_params: Dict[str, str]) -> List[str]:
        """Validate parameter substitution in CLAUDE.md. Returns list of errors."""
        errors = []
        
        claude_md = self.deployment_path / "CLAUDE.md"
        if not claude_md.exists():
            errors.append("CLAUDE.md not found for parameter validation")
            return errors
        
        content = claude_md.read_text()
        
        for param_name, expected_value in expected_params.items():
            if expected_value and expected_value not in content:
                errors.append(f"Parameter {param_name} value '{expected_value}' not found in CLAUDE.md")
        
        return errors
    
    def validate_executable_permissions(self) -> List[str]:
        """Validate shell scripts have executable permissions. Returns list of errors."""
        errors = []
        
        # Find all shell scripts
        shell_scripts = list(self.deployment_path.rglob("*.sh"))
        
        for script in shell_scripts:
            if not (script.stat().st_mode & 0o111):
                errors.append(f"Shell script not executable: {script.relative_to(self.deployment_path)}")
        
        return errors
    
    def get_full_validation_report(self, expected_params: Dict[str, str] = None) -> Dict[str, any]:
        """Get comprehensive validation report."""
        expected_params = expected_params or {}
        
        return {
            "directory_errors": self.validate_directory_structure(),
            "file_errors": self.validate_critical_files(),
            "file_counts": self.validate_file_counts(),
            "parameter_errors": self.validate_parameter_substitution(expected_params),
            "permission_errors": self.validate_executable_permissions()
        }


class TemporaryRepoFactory:
    """Factory for creating temporary test repositories with various configurations."""
    
    @staticmethod
    def create_empty_repo() -> Path:
        """Create empty temporary directory."""
        temp_dir = tempfile.mkdtemp(prefix="acforge_test_")
        return Path(temp_dir)
    
    @staticmethod 
    def create_git_repo() -> Path:
        """Create temporary directory with .git folder."""
        repo_path = TemporaryRepoFactory.create_empty_repo()
        (repo_path / ".git").mkdir()
        return repo_path
    
    @staticmethod
    def create_existing_acforge_config() -> Path:
        """Create repo with existing .acforge configuration."""
        repo_path = TemporaryRepoFactory.create_empty_repo()
        acforge_dir = repo_path / ".acforge"
        acforge_dir.mkdir()
        (acforge_dir / "state.json").write_text('{"version": "old"}')
        return repo_path
    
    @staticmethod
    def create_readonly_repo() -> Path:
        """Create read-only temporary directory."""
        repo_path = TemporaryRepoFactory.create_empty_repo()
        repo_path.chmod(0o444)
        return repo_path


def count_files_by_extension(base_path: Path) -> Dict[str, int]:
    """Count files by extension in a directory tree."""
    counts = {}
    
    for file_path in base_path.rglob("*"):
        if file_path.is_file():
            suffix = file_path.suffix.lower()
            counts[suffix] = counts.get(suffix, 0) + 1
    
    return counts


def find_files_containing_text(base_path: Path, text: str) -> List[Path]:
    """Find all text files containing specific text."""
    matching_files = []
    
    for file_path in base_path.rglob("*"):
        if file_path.is_file() and file_path.suffix in ['.md', '.json', '.sh', '.py', '.txt']:
            try:
                if text in file_path.read_text():
                    matching_files.append(file_path)
            except (UnicodeDecodeError, PermissionError):
                # Skip binary or inaccessible files
                continue
    
    return matching_files


def validate_json_files(base_path: Path) -> List[str]:
    """Validate that all JSON files are properly formatted. Returns list of errors."""
    import json
    
    errors = []
    
    for json_file in base_path.rglob("*.json"):
        try:
            json.loads(json_file.read_text())
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in {json_file.relative_to(base_path)}: {e}")
    
    return errors