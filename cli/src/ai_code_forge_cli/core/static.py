"""Static content resource access and management."""

import hashlib
from importlib import resources
from pathlib import Path
from typing import Dict, List, Optional

try:
    from importlib.resources.abc import Traversable
except ImportError:
    # Fallback for Python < 3.9
    from importlib.abc import Traversable


class StaticContentManager:
    """Manages static content resource access."""
    
    def __init__(self) -> None:
        """Initialize static content manager."""
        self.static_package = "ai_code_forge_cli.dist"
    
    def list_static_files(self) -> List[str]:
        """List all available static files.
        
        Returns:
            List of static file paths relative to dist root
        """
        static_files = []
        
        try:
            # Use importlib.resources to access bundled static content
            dist_root = resources.files(self.static_package)
            self._collect_files_recursive(dist_root, "", static_files)
        except (ImportError, FileNotFoundError):
            # Fallback to development mode - access dist directly
            dev_dist = Path(__file__).parent.parent.parent.parent.parent / "dist"
            if dev_dist.exists():
                for file_path in dev_dist.rglob("*"):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(dev_dist)
                        static_files.append(str(relative_path))
        
        return sorted(static_files)
    
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
    
    def get_static_content(self, static_path: str) -> Optional[bytes]:
        """Get content of a static file.
        
        Args:
            static_path: Path to static file relative to dist root
            
        Returns:
            Static content as bytes, or None if not found
        """
        try:
            # Try bundled static content first
            dist_root = resources.files(self.static_package)
            static_file = dist_root / static_path
            
            if static_file.is_file():
                return static_file.read_bytes()
        except (ImportError, FileNotFoundError, UnicodeDecodeError):
            pass
        
        # Fallback to development mode
        dev_static = Path(__file__).parent.parent.parent.parent.parent / "dist" / static_path
        if dev_static.exists() and dev_static.is_file():
            try:
                return dev_static.read_bytes()
            except Exception:
                pass
        
        return None


class StaticContentDeployer:
    """Handles deployment of static content to repository."""
    
    def __init__(self, target_path: Path, static_manager: StaticContentManager) -> None:
        """Initialize static content deployer.
        
        Args:
            target_path: Target repository path
            static_manager: Static content manager instance
        """
        self.target_path = target_path
        self.static_manager = static_manager
        self.acforge_dir = target_path / ".acforge"
    
    def deploy_static_content(self, dry_run: bool = False) -> Dict[str, any]:
        """Deploy all static content to the repository.
        
        Args:
            dry_run: If True, don't actually create files
            
        Returns:
            Dictionary with deployment results
        """
        results = {
            "files_deployed": [],
            "directories_created": [],
            "errors": []
        }
        
        try:
            # Ensure .acforge directory exists
            if not dry_run:
                self.acforge_dir.mkdir(exist_ok=True)
            if ".acforge/" not in results["directories_created"]:
                results["directories_created"].append(".acforge/")
            
            # Get all static files
            static_files = self.static_manager.list_static_files()
            
            for static_path in static_files:
                try:
                    # Get static content (no processing)
                    content = self.static_manager.get_static_content(static_path)
                    if content is None:
                        results["errors"].append(f"Could not read static file: {static_path}")
                        continue
                    
                    # Determine target path
                    target_file_path = self._get_target_path(static_path)
                    relative_path = target_file_path.relative_to(self.target_path)
                    
                    if not dry_run:
                        # Create parent directories
                        target_file_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Write file (no parameter substitution)
                        target_file_path.write_bytes(content)
                        
                        # Set executable permissions for shell scripts
                        if target_file_path.suffix == ".sh":
                            target_file_path.chmod(0o755)
                    
                    results["files_deployed"].append(str(relative_path))
                    
                except Exception as e:
                    results["errors"].append(f"Failed to deploy {static_path}: {e}")
        
        except Exception as e:
            results["errors"].append(f"Static deployment failed: {e}")
        
        return results
    
    def _get_target_path(self, static_path: str) -> Path:
        """Convert static path to target file path.
        
        Args:
            static_path: Static file path (e.g., "scripts/launch-claude.sh")
            
        Returns:
            Target file path in .acforge directory
        """
        # scripts/launch-claude.sh → .acforge/scripts/launch-claude.sh
        # mcp-servers/config.json → .acforge/mcp-servers/config.json
        return self.acforge_dir / static_path