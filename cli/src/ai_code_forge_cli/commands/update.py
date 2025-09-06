"""Update command implementation."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import click

from .. import __version__
from ..core.detector import RepositoryDetector
from ..core.deployer import TemplateDeployer
from ..core.git_wrapper import create_git_wrapper  
from ..core.state import StateManager
from ..core.static import StaticContentManager, StaticContentDeployer
from ..core.templates import TemplateManager


@click.command("update")
@click.argument(
    "target_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=False,
    default=".",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be updated without making changes"
)
@click.option(
    "--force", "-f",
    is_flag=True,
    help="Update even if conflicts are detected"
)
@click.option(
    "--no-preserve",
    is_flag=True,
    help="Do not preserve existing customizations"
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Show detailed progress information"
)
@click.pass_obj
def update_command(
    acf_ctx: Any,
    target_dir: Path,
    dry_run: bool,
    force: bool,
    no_preserve: bool,
    verbose: bool,
) -> None:
    """Update repository templates to latest version.
    
    Synchronizes templates in .claude/ directory with the latest bundled
    templates, preserving user customizations in .local files. Analyzes
    changes and conflicts before updating.
    
    TARGET_DIR: Target repository directory (defaults to current directory)
    
    Examples:
      acforge update                    # Update current directory
      acforge update /path/to/repo      # Update specific directory
      acforge update --dry-run          # Preview what would be updated
      acforge update --force            # Update even with conflicts
      acforge update --no-preserve      # Skip customization preservation
    """
    try:
        # Resolve target directory
        target_path = target_dir.resolve()
        
        if verbose or acf_ctx.verbose:
            click.echo(f"🎯 Target directory: {target_path}")
        
        # Execute update
        results = _run_update(
            target_path=target_path,
            dry_run=dry_run,
            force=force,
            preserve_customizations=not no_preserve,
            verbose=verbose or acf_ctx.verbose,
            acf_ctx=acf_ctx,
        )
        
        # Display results
        _display_results(results, dry_run, verbose or acf_ctx.verbose)
        
        # Set exit code based on success
        if not results["success"]:
            raise click.ClickException("Update failed")
    
    except Exception as e:
        if verbose or acf_ctx.verbose:
            raise
        else:
            raise click.ClickException(f"Failed to update repository: {e}")


def _run_update(
    target_path: Path,
    dry_run: bool = False,
    force: bool = False,
    preserve_customizations: bool = True,
    verbose: bool = False,
    acf_ctx: Any = None,
) -> Dict[str, Any]:
    """Execute the update command logic.
    
    Args:
        target_path: Target repository path
        dry_run: Show what would be updated without changes
        force: Update even if conflicts are detected
        preserve_customizations: Preserve .local files and customizations
        verbose: Show detailed output
        acf_ctx: CLI context object containing global flags
        
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
        "git_used": False,
        "pre_commit_made": False,
    }
    
    try:
        # Initialize components
        state_manager = StateManager(target_path)
        template_manager = TemplateManager()
        
        # Analyze what needs updating
        analysis = _analyze_changes(state_manager, template_manager, target_path)
        results["analysis"] = analysis
        
        if verbose:
            click.echo(f"📋 Analysis: {analysis['status']}")
        
        # Handle different status cases
        if analysis["status"] == "not_initialized":
            results["errors"].append("Repository not initialized. Run 'acforge init' first.")
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
        
        # Handle pre-update git commit if git integration is enabled
        if acf_ctx and acf_ctx.git and not dry_run:
            results["git_used"] = True
            git_wrapper = create_git_wrapper(acf_ctx, verbose)
            pre_commit_result = git_wrapper.commit_existing_state_before_init()  # Reuse same method
            if pre_commit_result["success"]:
                results["pre_commit_made"] = True
            elif verbose:
                click.echo(f"⚠️  Pre-update commit skipped: {pre_commit_result['error']}")
        
        # Preserve customizations before updating
        backups = {}
        if preserve_customizations and analysis["preserved_customizations"]:
            if not dry_run:
                backups = _preserve_customizations(
                    target_path, analysis["preserved_customizations"]
                )
            results["files_preserved"] = analysis["preserved_customizations"]
        
        # Perform template and static content updates
        update_results = _perform_update(
            target_path, state_manager, template_manager, analysis, dry_run, verbose
        )
        results["files_updated"] = update_results["files_updated"]
        results["errors"].extend(update_results["errors"])
        
        # Restore customizations
        if preserve_customizations and backups and not dry_run:
            restored = _restore_customizations(target_path, backups)
            if verbose:
                click.echo(f"📄 Restored {len(restored)} customizations")
        
        # Update state
        if not dry_run and not results["errors"]:
            _update_state(state_manager, template_manager, analysis)
        
        results["success"] = True
        if dry_run:
            results["message"] = f"Would update {len(results['files_updated'])} templates"
        else:
            results["message"] = f"Updated {len(results['files_updated'])} templates"
            
            # Handle git integration if requested
            if acf_ctx and acf_ctx.git and not dry_run:
                git_wrapper = create_git_wrapper(acf_ctx, verbose)
                current_state = state_manager.load_state()  # Fix: Load state properly
                old_version = current_state.installation.template_version if current_state and current_state.installation else None
                new_version = template_manager.calculate_bundle_checksum()[:8]
                
                git_result = git_wrapper.commit_command_changes(
                    command_name="update",
                    git_enabled=True,
                    old_version=old_version,
                    new_version=new_version
                )
                
                if git_result["success"]:
                    results["message"] += f" (committed: {git_result['commit_message']})"
                else:
                    results["warnings"] = results.get("warnings", [])
                    results["warnings"].append(f"Git commit failed: {git_result['error']}")
                    if verbose:
                        click.echo(f"🔧 Git integration failed: {git_result['error']}")
        
    except Exception as e:
        results["errors"].append(f"Update failed: {e}")
        results["message"] = f"Failed to update templates: {e}"
    
    return results


def _analyze_changes(state_manager: StateManager, template_manager: TemplateManager, target_path: Path) -> Dict[str, Any]:
    """Analyze what templates need updating."""
    current_state = state_manager.load_state()
    available_templates = template_manager.list_template_files()
    
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
    available_checksum = template_manager.calculate_bundle_checksum()
    
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
            available_info = template_manager.get_template_info(template_path)
            
            if available_info and current_info.checksum != available_info.checksum:
                analysis["updated_templates"].append(template_path)
    
    # Check for customization conflicts
    analysis["conflicts"], analysis["preserved_customizations"] = _analyze_conflicts(
        target_path, analysis["new_templates"] + analysis["updated_templates"]
    )
    
    return analysis


def _analyze_conflicts(target_path: Path, templates_to_update: List[str]) -> Tuple[List[str], List[str]]:
    """Analyze potential conflicts with customizations."""
    conflicts = []
    preserved = []
    
    claude_dir = target_path / ".claude"
    
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


def _preserve_customizations(target_path: Path, files_to_preserve: List[str]) -> Dict[str, str]:
    """Create backups of files that should be preserved."""
    backups = {}
    claude_dir = target_path / ".claude"
    backup_dir = target_path / ".acforge" / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for file_path in files_to_preserve:
        source_file = claude_dir / file_path
        if source_file.exists():
            backup_file = backup_dir / file_path
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file content
            backup_file.write_bytes(source_file.read_bytes())
            backups[file_path] = str(backup_file)
    
    return backups


def _restore_customizations(target_path: Path, backups: Dict[str, str]) -> List[str]:
    """Restore customizations from backups."""
    restored = []
    claude_dir = target_path / ".claude"
    
    for original_path, backup_path in backups.items():
        backup_file = Path(backup_path)
        target_file = claude_dir / original_path
        
        if backup_file.exists():
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_bytes(backup_file.read_bytes())
            restored.append(original_path)
    
    return restored


def _perform_update(
    target_path: Path,
    state_manager: StateManager,
    template_manager: TemplateManager,
    analysis: Dict[str, Any],
    dry_run: bool,
    verbose: bool
) -> Dict[str, Any]:
    """Perform the actual template updates."""
    results = {
        "files_updated": [],
        "errors": [],
    }
    
    # Get current state to extract parameters
    current_state = state_manager.load_state()
    
    # Prepare parameters for template substitution
    parameters = {}
    if current_state.installation:
        # Try to extract parameters from current installation
        repo_info = _detect_current_parameters(target_path)
        parameters = {
            "GITHUB_OWNER": repo_info.get("github_owner", "unknown"),
            "PROJECT_NAME": repo_info.get("project_name", "unknown"),
            "REPO_URL": repo_info.get("repo_url", "{{REPO_URL}}"),
            "CREATION_DATE": datetime.now().isoformat(),
            "ACF_VERSION": __version__,
            "TEMPLATE_VERSION": analysis["available_version"],
        }
    
    # Use TemplateDeployer to update templates
    template_deployer = TemplateDeployer(target_path, template_manager)
    
    # Filter templates to update
    templates_to_update = (
        analysis.get("new_templates", []) +
        analysis.get("updated_templates", [])
    )
    
    if verbose:
        click.echo(f"🔄 Updating {len(templates_to_update)} templates")
    
    # Deploy updated templates
    template_results = template_deployer.deploy_templates(parameters, dry_run)
    
    # Deploy static content (always update all static content)
    static_manager = StaticContentManager()
    static_deployer = StaticContentDeployer(target_path, static_manager)
    static_results = static_deployer.deploy_static_content(dry_run)
    
    if verbose:
        click.echo(f"🔄 Updating static content")
    
    # Combine results
    all_template_files = [
        f for f in template_results["files_deployed"]
        if any(template in f for template in templates_to_update)
    ]
    all_static_files = static_results["files_deployed"]
    
    results["files_updated"] = all_template_files + all_static_files
    results["errors"] = template_results["errors"] + static_results["errors"]
    
    return results


def _detect_current_parameters(target_path: Path) -> Dict[str, Optional[str]]:
    """Detect current repository parameters for template substitution."""
    detector = RepositoryDetector(target_path)
    return detector.detect_github_info()


def _update_state(
    state_manager: StateManager,
    template_manager: TemplateManager,
    analysis: Dict[str, Any]
) -> None:
    """Update ACF state after successful update."""
    with state_manager.atomic_update() as state:
        if state.installation:
            state.installation.template_version = analysis["available_version"]
            state.installation.installed_at = datetime.now()
            state.installation.cli_version = __version__
        
        # Update template checksums
        available_checksum = template_manager.calculate_bundle_checksum()
        if state.templates:
            state.templates.checksum = available_checksum
            
            # Update file information for all templates
            available_templates = template_manager.list_template_files()
            updated_files = {}
            
            for template_path in available_templates:
                template_info = template_manager.get_template_info(template_path)
                if template_info:
                    updated_files[template_path] = template_info
            
            state.templates.files = updated_files


def _display_results(results: dict, dry_run: bool, verbose: bool) -> None:
    """Display update results to user.
    
    Args:
        results: Results dictionary from UpdateCommand.run()
        dry_run: Whether this was a dry run
        verbose: Whether to show detailed output
    """
    if dry_run:
        click.echo("🔍 DRY RUN - No changes made")
        click.echo()
    
    analysis = results.get("analysis", {})
    
    if results["success"]:
        # Show update status
        status = analysis.get("status", "unknown")
        
        if status == "not_initialized":
            click.echo("❌ Repository not initialized")
            click.echo("💡 Run 'acforge init' first to set up ACForge configuration")
            return
        
        if status == "up_to_date":
            click.echo("✅ Templates are already up to date")
            if verbose and analysis.get("current_version"):
                click.echo(f"📦 Current version: {analysis['current_version']}")
            return
        
        if status == "update_available":
            if dry_run:
                click.echo("📋 Update preview:")
            else:
                click.echo("🎉 Templates updated successfully!")
            click.echo()
            
            # Show version information
            current_version = analysis.get("current_version", "unknown")
            available_version = analysis.get("available_version", "unknown")
            
            if verbose:
                click.echo(f"📦 Version: {current_version} → {available_version}")
                click.echo()
            
            # Show template changes
            new_templates = analysis.get("new_templates", [])
            updated_templates = analysis.get("updated_templates", [])
            removed_templates = analysis.get("removed_templates", [])
            
            if new_templates:
                click.echo(f"➕ New templates ({len(new_templates)}):")
                for template in new_templates[:5]:  # Show first 5
                    click.echo(f"  ✅ {template}")
                if len(new_templates) > 5:
                    click.echo(f"  ... and {len(new_templates) - 5} more")
                click.echo()
            
            if updated_templates:
                click.echo(f"🔄 Updated templates ({len(updated_templates)}):")
                for template in updated_templates[:5]:  # Show first 5
                    click.echo(f"  ✅ {template}")
                if len(updated_templates) > 5:
                    click.echo(f"  ... and {len(updated_templates) - 5} more")
                click.echo()
            
            if removed_templates:
                click.echo(f"➖ Removed templates ({len(removed_templates)}):")
                for template in removed_templates:
                    click.echo(f"  ❌ {template}")
                click.echo()
            
            # Show customization info
            preserved = results.get("files_preserved", [])
            if preserved:
                click.echo(f"🛡️  Customizations preserved ({len(preserved)}):")
                for custom_file in preserved[:3]:  # Show first 3
                    click.echo(f"  ✅ {custom_file}")
                if len(preserved) > 3:
                    click.echo(f"  ... and {len(preserved) - 3} more")
                click.echo()
            
            # Show summary
            files_updated = results.get("files_updated", [])
            if not dry_run and files_updated:
                click.echo("📦 Update summary:")
                click.echo(f"  ✅ {len(files_updated)} files updated")
                if preserved:
                    click.echo(f"  🛡️  {len(preserved)} customizations preserved")
                click.echo()
                
                # Show next steps
                click.echo("💡 Next steps:")
                click.echo("  - Run 'acforge status' to verify updates")
                click.echo("  - Review preserved customizations if needed")
                click.echo("  - Test your Claude Code configuration")
                
                # Show git rollback instructions if git was used
                if results.get("git_used", False):
                    click.echo()
                    click.echo("🔄 Git rollback options:")
                    if results.get("pre_commit_made", False):
                        click.echo("  - Undo update: git reset --hard HEAD~1")
                        click.echo("  - Keep changes but unstage: git reset --soft HEAD~1")
                    else:
                        click.echo("  - Undo update: git reset --hard HEAD~1")
                    click.echo("  - View changes: git log --oneline -3")
                
                click.echo()
                click.echo("🚀 Templates updated successfully!")
    else:
        # Show errors
        click.echo("❌ Update failed:")
        click.echo()
        
        for error in results["errors"]:
            click.echo(f"  ❌ {error}")
        
        if results["warnings"]:
            click.echo()
            click.echo("⚠️  Warnings:")
            for warning in results["warnings"]:
                click.echo(f"  ⚠️  {warning}")
        
        # Show conflicts if any
        conflicts = analysis.get("conflicts", [])
        if conflicts:
            click.echo()
            click.echo("⚠️  Customization conflicts detected:")
            for conflict in conflicts:
                click.echo(f"  ⚠️  {conflict}")
            click.echo()
            click.echo("💡 Use --force to proceed with updates")
        
        if results["message"]:
            click.echo()
            click.echo(f"💡 {results['message']}")
    
    # Always show warnings if any (for successful updates too)
    if results["warnings"] and results["success"]:
        click.echo()
        click.echo("⚠️  Warnings:")
        for warning in results["warnings"]:
            click.echo(f"  ⚠️  {warning}")