"""Template resource access and management."""

import hashlib
from importlib import resources
from pathlib import Path
from typing import Dict, List, Optional, Set

try:
    from importlib.resources.abc import Traversable
except ImportError:
    # Fallback for Python < 3.9
    from importlib.abc import Traversable

from .state import FileInfo


class TemplateManager:
    """Manages template resource access and validation."""
    
    def __init__(self) -> None:
        """Initialize template manager."""
        self.template_package = "ai_code_forge_cli.templates"
    
    def list_template_files(self) -> List[str]:
        """List all available template files.
        
        Returns:
            List of template file paths relative to templates root
        """
        template_files = []
        
        try:
            # Use importlib.resources to access bundled templates
            templates_root = resources.files(self.template_package)
            self._collect_files_recursive(templates_root, "", template_files)
        except (ImportError, FileNotFoundError):
            # Fallback to development mode - access templates directly
            dev_templates = Path(__file__).parent.parent.parent.parent.parent / "templates"
            if dev_templates.exists():
                for file_path in dev_templates.rglob("*"):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(dev_templates)
                        template_files.append(str(relative_path))
        
        return sorted(template_files)
    
    def _collect_files_recursive(self, directory: Traversable, prefix: str, files: List[str]) -> None:
        """Recursively collect files from a traversable directory.
        
        Args:
            directory: Traversable directory to scan
            prefix: Path prefix for current level
            files: List to append found files to
        """
        try:
            for item in directory.iterdir():
                item_path = f"{prefix}/{item.name}" if prefix else item.name
                
                if item.is_file():
                    files.append(item_path)
                elif item.is_dir():
                    self._collect_files_recursive(item, item_path, files)
        except (OSError, AttributeError):
            # Handle cases where directory iteration fails
            pass
    
    def get_template_content(self, template_path: str) -> Optional[str]:
        """Get content of a template file.
        
        Args:
            template_path: Path to template file relative to templates root
            
        Returns:
            Template content as string, or None if not found
        """
        try:
            # Try bundled templates first
            templates_root = resources.files(self.template_package)
            template_file = templates_root / template_path
            
            if template_file.is_file():
                return template_file.read_text(encoding="utf-8")
        except (ImportError, FileNotFoundError, UnicodeDecodeError):
            pass
        
        # Fallback to development mode
        dev_template = Path(__file__).parent.parent.parent.parent.parent / "templates" / template_path
        if dev_template.exists() and dev_template.is_file():
            try:
                return dev_template.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pass
        
        return None
    
    def get_template_info(self, template_path: str) -> Optional[FileInfo]:
        """Get information about a template file.
        
        Args:
            template_path: Path to template file relative to templates root
            
        Returns:
            FileInfo object with metadata, or None if not found
        """
        content = self.get_template_content(template_path)
        if content is None:
            return None
        
        content_bytes = content.encode("utf-8")
        checksum = hashlib.sha256(content_bytes).hexdigest()
        
        return FileInfo(
            checksum=checksum,
            customized=False,
            size=len(content_bytes)
        )
    
    def calculate_bundle_checksum(self) -> str:
        """Calculate checksum for entire template bundle.
        
        Returns:
            SHA256 checksum of all template files combined
        """
        hasher = hashlib.sha256()
        
        for template_path in self.list_template_files():
            content = self.get_template_content(template_path)
            if content:
                hasher.update(f"{template_path}:".encode("utf-8"))
                hasher.update(content.encode("utf-8"))
        
        return hasher.hexdigest()
    
    def validate_templates(self) -> Dict[str, str]:
        """Validate template bundle integrity.
        
        Returns:
            Dictionary mapping any problematic template paths to error messages
        """
        errors = {}
        template_files = self.list_template_files()
        
        if not template_files:
            errors["_bundle"] = "No template files found"
            return errors
        
        for template_path in template_files:
            content = self.get_template_content(template_path)
            if content is None:
                errors[template_path] = "Could not read template file"
            elif not content.strip():
                errors[template_path] = "Template file is empty"
        
        return errors


class RepositoryAnalyzer:
    """Analyzes repository configuration state."""
    
    def __init__(self, repo_root: Path) -> None:
        """Initialize repository analyzer.
        
        Args:
            repo_root: Root directory of the repository
        """
        self.repo_root = repo_root
        self.claude_dir = repo_root / ".claude"
        self.acf_dir = repo_root / ".acforge"
    
    def detect_configuration_type(self) -> str:
        """Detect what type of configuration exists in repository.
        
        Returns:
            Configuration type: 'acforge', 'claude', 'mixed', or 'none'
        """
        has_acf = self.acf_dir.exists()
        has_claude = self.claude_dir.exists()
        
        if has_acf and has_claude:
            return "mixed"
        elif has_acf:
            return "acforge"
        elif has_claude:
            return "claude"
        else:
            return "none"
    
    def get_existing_files(self) -> Set[str]:
        """Get set of existing configuration files in repository.
        
        Returns:
            Set of configuration file paths relative to repository root
        """
        existing_files = set()
        
        # Check .claude directory
        if self.claude_dir.exists():
            for file_path in self.claude_dir.rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(self.repo_root)
                    existing_files.add(str(relative_path))
        
        # Check .acforge directory (but not state files)
        if self.acf_dir.exists():
            for file_path in self.acf_dir.rglob("*"):
                if file_path.is_file() and not file_path.name.endswith((".json", ".backup", ".tmp")):
                    relative_path = file_path.relative_to(self.repo_root)
                    existing_files.add(str(relative_path))
        
        return existing_files
    
    def find_customized_files(self) -> List[str]:
        """Find files that appear to be customized (.local files, etc.).
        
        Returns:
            List of customized file paths
        """
        customized = []
        
        for config_dir in [self.claude_dir, self.acf_dir]:
            if config_dir.exists():
                for file_path in config_dir.rglob("*.local.*"):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(self.repo_root)
                        customized.append(str(relative_path))
        
        return customized
    
    def get_repository_info(self) -> Dict[str, any]:
        """Get general repository information.
        
        Returns:
            Dictionary with repository metadata
        """
        git_dir = self.repo_root / ".git"
        
        return {
            "is_git_repo": git_dir.exists(),
            "repo_root": str(self.repo_root),
            "has_claude_config": self.claude_dir.exists(),
            "has_acf_config": self.acf_dir.exists(),
            "config_type": self.detect_configuration_type(),
            "existing_files_count": len(self.get_existing_files()),
            "customized_files_count": len(self.find_customized_files()),
        }