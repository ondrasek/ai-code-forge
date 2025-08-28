"""Template update and synchronization functionality."""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import click

from .. import __version__
from .init import ParameterSubstitutor, TemplateDeployer
from .state import StateManager
from .templates import TemplateManager


class UpdateAnalyzer:
    """Analyzes template changes and conflicts for updates."""
    
    def __init__(self, state_manager: StateManager, template_manager: TemplateManager) -> None:
        """Initialize update analyzer.
        
        Args:
            state_manager: State manager instance
            template_manager: Template manager instance
        """
        self.state_manager = state_manager
        self.template_manager = template_manager
    
    def analyze_changes(self) -> Dict[str, Any]:
        """Analyze what templates need updating.
        
        Returns:
            Dictionary with analysis results
        """
        current_state = self.state_manager.load_state()
        available_templates = self.template_manager.list_template_files()
        
        analysis = {
            "status": "unknown",
            "current_version": None,
            "available_version": None,
            "needs_update": False,
            "new_templates": [],
            "updated_templates": [],
            "removed_templates": [],
            "conflicts": [],
            "preserved_customizations": [],
        }
        
        # Check if ACF has been initialized
        if current_state.installation is None:
            analysis["status"] = "not_initialized"
            return analysis
        
        # Get version information
        current_checksum = current_state.templates.checksum if current_state.templates else ""
        available_checksum = self.template_manager.calculate_bundle_checksum()
        
        analysis["current_version"] = current_checksum[:8] if current_checksum else "unknown"
        analysis["available_version"] = available_checksum[:8]
        
        # Check if update is needed
        if current_checksum == available_checksum:
            analysis["status"] = "up_to_date"
            return analysis
        
        analysis["needs_update"] = True
        analysis["status"] = "update_available"
        
        # Analyze individual template changes
        current_templates = set(current_state.templates.files.keys()) if current_state.templates else set()
        available_templates_set = set(available_templates)
        
        # Find new templates
        analysis["new_templates"] = list(available_templates_set - current_templates)
        
        # Find removed templates
        analysis["removed_templates"] = list(current_templates - available_templates_set)
        
        # Find updated templates
        for template_path in available_templates:
            if template_path in current_templates:
                current_info = current_state.templates.files[template_path]
                available_info = self.template_manager.get_template_info(template_path)
                
                if available_info and current_info.checksum != available_info.checksum:
                    analysis["updated_templates"].append(template_path)
        
        # Check for customization conflicts
        analysis["conflicts"], analysis["preserved_customizations"] = self._analyze_conflicts(
            analysis["new_templates"] + analysis["updated_templates"]
        )
        
        return analysis
    
    def _analyze_conflicts(self, templates_to_update: List[str]) -> Tuple[List[str], List[str]]:
        """Analyze potential conflicts with customizations.
        
        Args:
            templates_to_update: List of templates that will be updated
            
        Returns:
            Tuple of (conflicts, preserved_customizations)
        """
        conflicts = []
        preserved = []
        
        repo_root = self.state_manager.repo_root
        claude_dir = repo_root / ".claude"
        
        if not claude_dir.exists():
            return conflicts, preserved
        
        # Find .local files that correspond to templates being updated
        for local_file in claude_dir.rglob("*.local.*"):
            # Check if this local file corresponds to a template being updated
            relative_path = local_file.relative_to(claude_dir)
            base_name = str(relative_path).replace(".local", "")
            
            # Check if the base template is being updated
            template_matches = [
                t for t in templates_to_update 
                if base_name in t or t.endswith(base_name)
            ]
            
            if template_matches:
                preserved.append(str(relative_path))
                
                # Check if the local file might conflict with template changes
                if local_file.stat().st_size > 0:  # Non-empty local file
                    conflicts.append(str(relative_path))
        
        return conflicts, preserved


class CustomizationPreserver:
    """Handles preservation of user customizations during updates."""
    
    def __init__(self, repo_root: Path) -> None:
        """Initialize customization preserver.
        
        Args:
            repo_root: Repository root directory
        """
        self.repo_root = repo_root
        self.claude_dir = repo_root / ".claude"
    
    def identify_customizations(self) -> Dict[str, Any]:
        """Identify existing customizations in the repository.
        
        Returns:
            Dictionary with customization information
        """
        customizations = {
            "local_files": [],
            "modified_files": [],
            "custom_files": [],
        }
        
        if not self.claude_dir.exists():
            return customizations
        
        # Find .local files
        for local_file in self.claude_dir.rglob("*.local.*"):
            relative_path = local_file.relative_to(self.claude_dir)
            customizations["local_files"].append(str(relative_path))
        
        # Find custom files (files not from templates)
        # This is a simplified check - in practice, we'd compare against known templates
        for custom_file in self.claude_dir.rglob("*"):
            if custom_file.is_file() and ".local" not in custom_file.name:
                relative_path = custom_file.relative_to(self.claude_dir)
                if str(relative_path).startswith("custom/"):
                    customizations["custom_files"].append(str(relative_path))
        
        return customizations
    
    def preserve_during_update(self, files_to_preserve: List[str]) -> Dict[str, str]:
        """Create backups of files that should be preserved.
        
        Args:
            files_to_preserve: List of file paths to preserve
            
        Returns:
            Dictionary mapping original paths to backup paths
        """
        backups = {}
        backup_dir = self.repo_root / ".acf" / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for file_path in files_to_preserve:
            source_file = self.claude_dir / file_path
            if source_file.exists():
                backup_file = backup_dir / file_path
                backup_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file content
                backup_file.write_bytes(source_file.read_bytes())
                backups[file_path] = str(backup_file)
        
        return backups
    
    def restore_customizations(self, backups: Dict[str, str]) -> List[str]:
        """Restore customizations from backups.
        
        Args:
            backups: Dictionary mapping original paths to backup paths
            
        Returns:
            List of files that were restored
        """
        restored = []
        
        for original_path, backup_path in backups.items():
            backup_file = Path(backup_path)
            target_file = self.claude_dir / original_path
            
            if backup_file.exists():
                target_file.parent.mkdir(parents=True, exist_ok=True)
                target_file.write_bytes(backup_file.read_bytes())
                restored.append(original_path)
        
        return restored


class UpdateCommand:
    """Implements the acf update command."""
    
    def __init__(self, target_path: Path) -> None:
        """Initialize update command.
        
        Args:
            target_path: Target repository path
        """
        self.target_path = target_path
        self.state_manager = StateManager(target_path)
        self.template_manager = TemplateManager()
        self.analyzer = UpdateAnalyzer(self.state_manager, self.template_manager)
        self.preserver = CustomizationPreserver(target_path)
    
    def run(
        self,
        dry_run: bool = False,
        force: bool = False,
        preserve_customizations: bool = True,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """Execute the update command.
        
        Args:
            dry_run: Show what would be updated without changes
            force: Update even if conflicts are detected
            preserve_customizations: Preserve .local files and customizations
            verbose: Show detailed output
            
        Returns:
            Dictionary with command results
        """
        results = {
            "success": False,
            "message": "",
            "analysis": {},
            "files_updated": [],
            "files_preserved": [],
            "warnings": [],
            "errors": [],
        }
        
        try:
            # Analyze what needs updating
            analysis = self.analyzer.analyze_changes()
            results["analysis"] = analysis
            
            if verbose:
                click.echo(f"📋 Analysis: {analysis['status']}")
            
            # Handle different status cases
            if analysis["status"] == "not_initialized":
                results["errors"].append("Repository not initialized. Run 'acf init' first.")
                return results
            
            if analysis["status"] == "up_to_date":
                results["success"] = True
                results["message"] = "Templates are already up to date"
                return results
            
            if not analysis["needs_update"]:
                results["success"] = True
                results["message"] = "No updates needed"
                return results
            
            # Check for conflicts
            if analysis["conflicts"] and not force:
                results["warnings"].extend([
                    f"Customization conflict detected: {conflict}" 
                    for conflict in analysis["conflicts"]
                ])
                results["warnings"].append(
                    "Use --force to proceed with updates (customizations will be preserved)"
                )
                results["errors"].append(
                    "Conflicts detected. Review conflicts and use --force if you want to proceed."
                )
                return results
            
            # Preserve customizations before updating
            backups = {}
            if preserve_customizations and analysis["preserved_customizations"]:
                if not dry_run:
                    backups = self.preserver.preserve_during_update(
                        analysis["preserved_customizations"]
                    )
                results["files_preserved"] = analysis["preserved_customizations"]
            
            # Perform template updates
            update_results = self._perform_update(analysis, dry_run, verbose)
            results["files_updated"] = update_results["files_updated"]
            results["errors"].extend(update_results["errors"])
            
            # Restore customizations
            if preserve_customizations and backups and not dry_run:
                restored = self.preserver.restore_customizations(backups)
                if verbose:
                    click.echo(f"📄 Restored {len(restored)} customizations")
            
            # Update state
            if not dry_run and not results["errors"]:
                self._update_state(analysis)
            
            results["success"] = True
            if dry_run:
                results["message"] = f"Would update {len(results['files_updated'])} templates"
            else:
                results["message"] = f"Updated {len(results['files_updated'])} templates"
            
        except Exception as e:
            results["errors"].append(f"Update failed: {e}")
            results["message"] = f"Failed to update templates: {e}"
        
        return results
    
    def _perform_update(self, analysis: Dict[str, Any], dry_run: bool, verbose: bool) -> Dict[str, Any]:
        """Perform the actual template updates.
        
        Args:
            analysis: Update analysis results
            dry_run: Whether this is a dry run
            verbose: Whether to show verbose output
            
        Returns:
            Dictionary with update results
        """
        results = {
            "files_updated": [],
            "errors": [],
        }
        
        # Get current state to extract parameters
        current_state = self.state_manager.load_state()
        
        # Prepare parameters for template substitution
        parameters = {}
        if current_state.installation:
            # Try to extract parameters from current installation
            # For now, use basic detection - could be enhanced
            repo_info = self._detect_current_parameters()
            parameters = {
                "GITHUB_OWNER": repo_info.get("github_owner", "unknown"),
                "PROJECT_NAME": repo_info.get("project_name", "unknown"),
                "REPO_URL": repo_info.get("repo_url", "{{REPO_URL}}"),
                "CREATION_DATE": datetime.now().isoformat(),
                "ACF_VERSION": __version__,
                "TEMPLATE_VERSION": analysis["available_version"],
            }
        
        # Use TemplateDeployer to update templates
        deployer = TemplateDeployer(self.target_path, self.template_manager)
        
        # Filter templates to update
        templates_to_update = (
            analysis.get("new_templates", []) +
            analysis.get("updated_templates", [])
        )
        
        if verbose:
            click.echo(f"🔄 Updating {len(templates_to_update)} templates")
        
        # Deploy updated templates
        deploy_results = deployer.deploy_templates(parameters, dry_run)
        
        results["files_updated"] = [
            f for f in deploy_results["files_deployed"]
            if any(template in f for template in templates_to_update)
        ]
        results["errors"] = deploy_results["errors"]
        
        return results
    
    def _detect_current_parameters(self) -> Dict[str, Optional[str]]:
        """Detect current repository parameters for template substitution.
        
        Returns:
            Dictionary with repository parameters
        """
        # This is a simplified implementation
        # In practice, you might want to store parameters in state or re-detect
        from .init import RepositoryDetector
        
        detector = RepositoryDetector(self.target_path)
        return detector.detect_github_info()
    
    def _update_state(self, analysis: Dict[str, Any]) -> None:
        """Update ACF state after successful update.
        
        Args:
            analysis: Update analysis results
        """
        with self.state_manager.atomic_update() as state:
            if state.installation:
                state.installation.template_version = analysis["available_version"]
                state.installation.installed_at = datetime.now()
                state.installation.cli_version = __version__
            
            # Update template checksums
            available_checksum = self.template_manager.calculate_bundle_checksum()
            if state.templates:
                state.templates.checksum = available_checksum
                
                # Update file information for all templates
                available_templates = self.template_manager.list_template_files()
                updated_files = {}
                
                for template_path in available_templates:
                    template_info = self.template_manager.get_template_info(template_path)
                    if template_info:
                        updated_files[template_path] = template_info
                
                state.templates.files = updated_files