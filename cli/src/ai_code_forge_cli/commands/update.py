"""Update command implementation."""

from pathlib import Path
from typing import Any

import click

from ..core.update import UpdateCommand


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
      acf update                    # Update current directory
      acf update /path/to/repo      # Update specific directory
      acf update --dry-run          # Preview what would be updated
      acf update --force            # Update even with conflicts
      acf update --no-preserve      # Skip customization preservation
    """
    try:
        # Resolve target directory
        target_path = target_dir.resolve()
        
        if verbose or acf_ctx.verbose:
            click.echo(f"🎯 Target directory: {target_path}")
        
        # Create update command instance
        update_cmd = UpdateCommand(target_path)
        
        # Execute update
        results = update_cmd.run(
            dry_run=dry_run,
            force=force,
            preserve_customizations=not no_preserve,
            verbose=verbose or acf_ctx.verbose,
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
            click.echo("💡 Run 'acf init' first to set up ACF configuration")
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
                click.echo("  - Run 'acf status' to verify updates")
                click.echo("  - Review preserved customizations if needed")
                click.echo("  - Test your Claude Code configuration")
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