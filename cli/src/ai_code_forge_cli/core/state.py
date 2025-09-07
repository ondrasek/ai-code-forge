"""State management for AI Code Forge CLI."""

import json
import shutil
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

from pydantic import BaseModel, Field


class InstallationState(BaseModel):
    """Installation state tracking."""
    
    template_version: str = Field(description="Version of templates currently installed")
    installed_at: datetime = Field(description="Timestamp when templates were installed")
    cli_version: str = Field(description="Version of CLI that performed installation")


class FileInfo(BaseModel):
    """Information about a template file."""
    
    checksum: str = Field(description="SHA256 checksum of file content")
    customized: bool = Field(default=False, description="Whether file has been customized")
    size: int = Field(description="File size in bytes")


class TemplateState(BaseModel):
    """Template state tracking."""
    
    checksum: str = Field(default="", description="Overall checksum of template bundle")
    files: Dict[str, FileInfo] = Field(default_factory=dict, description="Per-file information")


class CustomizationState(BaseModel):
    """Customization state tracking."""
    
    preserved_files: List[str] = Field(
        default_factory=list, 
        description="List of .local files that should be preserved"
    )
    custom_overrides: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Custom configuration overrides"
    )


class ACForgeState(BaseModel):
    """Complete ACForge state representation."""
    
    version: str = Field(default="1.0", description="State format version")
    installation: Optional[InstallationState] = Field(
        default=None, 
        description="Installation state information"
    )
    templates: TemplateState = Field(
        default_factory=TemplateState, 
        description="Template state information"
    )
    customizations: CustomizationState = Field(
        default_factory=CustomizationState, 
        description="User customization state"
    )


class StateManager:
    """Manages ACForge state file operations with atomic guarantees."""
    
    def __init__(self, repo_root: Path) -> None:
        """Initialize state manager for a repository.
        
        Args:
            repo_root: Root directory of the repository
        """
        self.repo_root = repo_root
        self.acforge_dir = repo_root / ".acforge"
        self.state_file = self.acforge_dir / "state.json"
        self.backup_file = self.state_file.with_suffix(".json.backup")
    
    def ensure_acforge_dir(self) -> None:
        """Ensure .acforge directory exists."""
        self.acforge_dir.mkdir(exist_ok=True)
    
    def load_state(self) -> ACForgeState:
        """Load current state from file.
        
        Returns:
            Current ACF state, or default state if no file exists
        """
        if not self.state_file.exists():
            return ACForgeState()
        
        try:
            with self.state_file.open(encoding="utf-8") as f:
                data = json.load(f)
            return ACForgeState.model_validate(data)
        except (json.JSONDecodeError, Exception) as e:
            # If main state is corrupted, try backup
            if self.backup_file.exists():
                try:
                    with self.backup_file.open(encoding="utf-8") as f:
                        data = json.load(f)
                    return ACForgeState.model_validate(data)
                except Exception:
                    pass
            
            # Return default state if both files are corrupted
            return ACForgeState()
    
    def save_state(self, state: ACForgeState) -> None:
        """Save state to file with atomic operation.
        
        Args:
            state: State to save
        """
        self.ensure_acforge_dir()
        
        # Write to temporary file first
        temp_file = self.state_file.with_suffix(".json.tmp")
        
        with temp_file.open("w", encoding="utf-8") as f:
            json.dump(
                state.model_dump(mode="json", exclude_none=False),
                f,
                indent=2,
                ensure_ascii=False
            )
        
        # Create backup of existing file
        if self.state_file.exists():
            shutil.copy2(self.state_file, self.backup_file)
        
        # Atomic move from temp to final location
        temp_file.replace(self.state_file)
    
    @contextmanager
    def atomic_update(self) -> Generator[ACForgeState, None, None]:
        """Context manager for atomic state updates.
        
        Yields:
            Current state for modification
        """
        state = self.load_state()
        original_backup_exists = self.backup_file.exists()
        
        # Create backup before modification
        if self.state_file.exists():
            shutil.copy2(self.state_file, self.backup_file)
        
        try:
            yield state
            self.save_state(state)
        except Exception:
            # Restore from backup on failure
            if self.backup_file.exists():
                shutil.copy2(self.backup_file, self.state_file)
            raise
        finally:
            # Clean up backup if it didn't exist originally
            if not original_backup_exists and self.backup_file.exists():
                try:
                    self.backup_file.unlink()
                except OSError:
                    pass  # Ignore cleanup failures
    
    def get_state_info(self) -> Dict[str, Any]:
        """Get basic state file information.
        
        Returns:
            Dictionary with state file metadata
        """
        info = {
            "state_file_exists": self.state_file.exists(),
            "acforge_dir_exists": self.acforge_dir.exists(),
            "backup_exists": self.backup_file.exists(),
        }
        
        if self.state_file.exists():
            stat = self.state_file.stat()
            info.update({
                "state_file_size": stat.st_size,
                "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
        
        return info