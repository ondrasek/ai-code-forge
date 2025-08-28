"""Init command implementation."""

from pathlib import Path
from typing import Any

import click

from ..core.init import InitCommand


@click.command("init")
@click.argument(
    "target_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=False,
    default=".",
)
@click.option(
    "--force", "-f",
    is_flag=True,
    help="Overwrite existing configuration without prompting"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be created without making changes"
)
@click.option(
    "--interactive", "-i",
    is_flag=True,
    help="Prompt for template parameters interactively"
)
@click.option(
    "--github-owner",
    type=str,
    help="Override GitHub owner detection"
)
@click.option(
    "--project-name",
    type=str,
    help="Override project name detection"
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Show detailed progress information"
)
@click.pass_obj
def init_command(
    acf_ctx: Any,
    target_dir: Path,
    force: bool,
    dry_run: bool,
    interactive: bool,
    github_owner: str,
    project_name: str,
    verbose: bool,
) -> None:
    """Initialize repository with ACF configuration and Claude Code templates.
    
    Creates .acf/ directory for ACF state management and .claude/ directory
    with Claude Code configuration from bundled templates. Performs template
    parameter substitution for repository-specific values.
    
    TARGET_DIR: Target repository directory (defaults to current directory)
    
    Examples:
      acf init                    # Initialize current directory
      acf init /path/to/repo      # Initialize specific directory  
      acf init --dry-run          # Preview what would be created
      acf init --force            # Overwrite existing configuration
      acf init --interactive      # Prompt for all parameters
    """
    try:
        # Resolve target directory
        target_path = target_dir.resolve()
        
        if verbose or acf_ctx.verbose:
            click.echo(f"🎯 Target directory: {target_path}")
        
        # Create init command instance
        init_cmd = InitCommand(target_path)
        
        # Execute initialization
        results = init_cmd.run(
            force=force,
            dry_run=dry_run,
            interactive=interactive,
            github_owner=github_owner,
            project_name=project_name,
            verbose=verbose or acf_ctx.verbose,
        )
        
        # Display results
        _display_results(results, dry_run, verbose or acf_ctx.verbose)
        
        # Set exit code based on success
        if not results["success"]:
            raise click.ClickException("Initialization failed")
    
    except Exception as e:
        if verbose or acf_ctx.verbose:
            raise
        else:
            raise click.ClickException(f"Failed to initialize repository: {e}")


def _display_results(results: dict, dry_run: bool, verbose: bool) -> None:
    """Display initialization results to user.
    
    Args:
        results: Results dictionary from InitCommand.run()
        dry_run: Whether this was a dry run
        verbose: Whether to show detailed output
    """
    if dry_run:
        click.echo("🔍 DRY RUN - No changes made")
        click.echo()
    
    if results["success"]:
        if dry_run:
            click.echo("✅ Repository initialization preview:")
        else:
            click.echo("🎉 ACF initialization complete!")
        click.echo()
        
        # Show files that would be/were created
        if results["files_created"]:
            if dry_run:
                click.echo("📁 Directories and files that would be created:")
            else:
                click.echo("📁 Created directories and files:")
            
            directories = [f for f in results["files_created"] if f.endswith("/")]
            files = [f for f in results["files_created"] if not f.endswith("/")]
            
            for directory in sorted(directories):
                click.echo(f"  ✅ {directory}")
            
            for file_path in sorted(files):
                click.echo(f"  ✅ {file_path}")
            
            click.echo()
        
        # Show parameters used
        if results["parameters_used"] and verbose:
            click.echo("🔧 Template parameters:")
            for key, value in results["parameters_used"].items():
                click.echo(f"  ✅ {key}: {value}")
            click.echo()
        
        # Show summary statistics
        file_count = len([f for f in results["files_created"] if not f.endswith("/")])
        dir_count = len([f for f in results["files_created"] if f.endswith("/")])
        
        if not dry_run:
            click.echo("📦 Deployment summary:")
            if dir_count:
                click.echo(f"  ✅ {dir_count} directories created")
            if file_count:
                click.echo(f"  ✅ {file_count} files deployed")
            
            if results["parameters_used"]:
                param_count = len([v for v in results["parameters_used"].values() if not v.startswith("{{")])
                click.echo(f"  ✅ {param_count} parameters substituted")
            
            click.echo()
            
            # Show next steps
            click.echo("💡 Next steps:")
            click.echo("  - Run 'acf status' to verify configuration")
            click.echo("  - Open repository in Claude Code to test setup")
            click.echo("  - Customize templates by creating .local files")
            click.echo("  - Use 'acf update' to sync with latest templates")
            click.echo()
            click.echo("🚀 Repository ready for AI-enhanced development!")
    else:
        # Show errors
        click.echo("❌ Initialization failed:")
        click.echo()
        
        for error in results["errors"]:
            click.echo(f"  ❌ {error}")
        
        if results["warnings"]:
            click.echo()
            click.echo("⚠️  Warnings:")
            for warning in results["warnings"]:
                click.echo(f"  ⚠️  {warning}")
        
        if results["message"]:
            click.echo()
            click.echo(f"💡 {results['message']}")
    
    # Always show warnings if any
    if results["warnings"] and results["success"]:
        click.echo()
        click.echo("⚠️  Warnings:")
        for warning in results["warnings"]:
            click.echo(f"  ⚠️  {warning}")