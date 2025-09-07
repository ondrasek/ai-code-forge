"""Init command implementation."""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import click

from .. import __version__
from ..core.detector import RepositoryDetector
from ..core.deployer import TemplateDeployer
from ..core.git_wrapper import create_git_wrapper
from ..core.state import ACForgeState, FileInfo, InstallationState, StateManager, TemplateState
from ..core.static import StaticContentManager
from ..core.templates import TemplateManager


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
    verbose: bool,
) -> None:
    """Initialize repository with ACF configuration and Claude Code templates.
    
    Creates .acforge/ directory for ACF state management and .claude/ directory
    with Claude Code configuration from bundled templates. Performs template
    parameter substitution for repository-specific values.
    
    TARGET_DIR: Target repository directory (defaults to current directory)
    
    Examples:
      acforge init                    # Initialize current directory
      acforge init /path/to/repo      # Initialize specific directory  
      acforge init --dry-run          # Preview what would be created
      acforge init --force            # Overwrite existing configuration
      acforge init --interactive      # Prompt for all parameters
    """
    try:
        # Resolve target directory - use original shell PWD for relative paths
        # to handle cases where uv run --directory changes the Python CWD
        if target_dir.is_absolute():
            target_path = target_dir.resolve()
        else:
            # For relative paths, resolve against original shell working directory
            original_pwd = os.environ.get('PWD', os.getcwd())
            target_path = (Path(original_pwd) / target_dir).resolve()
        
        if verbose or acf_ctx.verbose:
            click.echo(f"🎯 Target directory: {target_path}")
        
        # Execute initialization
        results = _run_init(
            target_path=target_path,
            force=force,
            dry_run=dry_run,
            interactive=interactive,
            verbose=verbose or acf_ctx.verbose,
            acf_ctx=acf_ctx,
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


def _run_init(
    target_path: Path,
    force: bool = False,
    dry_run: bool = False,
    interactive: bool = False,
    verbose: bool = False,
    acf_ctx: Any = None,
) -> Dict[str, Any]:
    """Execute the init command logic.
    
    Args:
        target_path: Target repository path
        force: Overwrite existing configuration
        dry_run: Show what would be done without changes
        interactive: Prompt for parameters
        verbose: Show detailed output
        acf_ctx: CLI context object containing global flags
        
    Returns:
        Dictionary with command results
    """
    results = {
        "success": False,
        "message": "",
        "files_created": [],
        "parameters_used": {},
        "warnings": [],
        "errors": [],
        "git_used": False,
        "pre_commit_made": False,
    }
    
    try:
        # Validate target directory
        if not target_path.exists():
            results["errors"].append(f"Target directory does not exist: {target_path}")
            return results
        
        # Initialize components
        detector = RepositoryDetector(target_path)
        template_manager = TemplateManager()
        static_manager = StaticContentManager()
        state_manager = StateManager(target_path)
        
        # Check existing configuration
        existing_config = detector.check_existing_configuration()
        
        if not force and (existing_config["has_acf"] or existing_config["has_claude"]):
            error_msg = "Repository already has ACF or Claude Code configuration. Use --force to overwrite."
            results["errors"].append(error_msg)
            return results
        
        # Detect repository information
        repo_info = detector.detect_github_info()
        
        # Repository info detection complete - no manual overrides
        
        # Prepare template parameters
        parameters = {
            "GITHUB_OWNER": repo_info.get("github_owner", "{{GITHUB_OWNER}}"),
            "PROJECT_NAME": repo_info.get("project_name", "{{PROJECT_NAME}}"),
            "REPO_URL": repo_info.get("repo_url", "{{REPO_URL}}"),
            "CREATION_DATE": datetime.now().isoformat(),
            "ACF_VERSION": __version__,
            "TEMPLATE_VERSION": template_manager.calculate_bundle_checksum()[:8],
        }
        
        # Handle interactive mode
        if interactive:
            parameters = _prompt_for_parameters(parameters)
        
        results["parameters_used"] = parameters
        
        if verbose:
            click.echo(f"🔧 Using parameters: {list(parameters.keys())}")
        
        # Handle pre-init git commit if git integration is enabled
        if acf_ctx and acf_ctx.git and not dry_run:
            results["git_used"] = True
            # Set repo_root to target_path for git operations
            original_repo_root = acf_ctx.repo_root
            acf_ctx.repo_root = target_path
            try:
                git_wrapper = create_git_wrapper(acf_ctx, verbose)
                pre_commit_result = git_wrapper.commit_existing_state_before_init()
                if pre_commit_result["success"]:
                    results["pre_commit_made"] = True
                elif verbose:
                    click.echo(f"⚠️  Pre-init commit skipped: {pre_commit_result['error']}")
            finally:
                # Restore original repo_root
                acf_ctx.repo_root = original_repo_root
        
        # Deploy templates
        template_deployer = TemplateDeployer(target_path, template_manager)
        template_results = template_deployer.deploy_templates(parameters, dry_run)
        
        # Note: Static content deployment removed - CLI now focuses on templates only
        # MCP servers and scripts are available as standalone repo components
        static_results = {"files_deployed": [], "directories_created": [], "errors": []}
        
        # Combine results
        results["files_created"] = (
            template_results["files_deployed"] + template_results["directories_created"] +
            static_results["files_deployed"] + static_results["directories_created"]
        )
        results["errors"].extend(template_results["errors"])
        results["errors"].extend(static_results["errors"])
        
        # Initialize ACF state (if not dry run)
        if not dry_run and not results["errors"]:
            _initialize_acf_state(state_manager, template_manager, parameters)
            results["files_created"].append(".acforge/state.json")
        
        if not results["errors"]:
            results["success"] = True
            if dry_run:
                results["message"] = f"Would create {len(results['files_created'])} files"
            else:
                results["message"] = "Repository initialized successfully"
                
                # Handle git integration if requested
                if acf_ctx and acf_ctx.git and not dry_run:
                    # Set repo_root to target_path for git operations
                    original_repo_root = acf_ctx.repo_root
                    acf_ctx.repo_root = target_path
                    try:
                        git_wrapper = create_git_wrapper(acf_ctx, verbose)
                        old_version = git_wrapper.get_current_version()
                        new_version = parameters.get("TEMPLATE_VERSION", "unknown")
                        
                        git_result = git_wrapper.commit_command_changes(
                            command_name="init",
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
                    finally:
                        # Restore original repo_root
                        acf_ctx.repo_root = original_repo_root
        else:
            results["message"] = "Initialization completed with errors"
            
    except Exception as e:
        results["errors"].append(f"Initialization failed: {e}")
        results["message"] = f"Failed to initialize repository: {e}"
    
    return results


def _prompt_for_parameters(parameters: Dict[str, str]) -> Dict[str, str]:
    """Prompt user for template parameters interactively.
    
    Args:
        parameters: Default parameters
        
    Returns:
        Updated parameters with user input
    """
    updated = parameters.copy()
    
    # Prompt for key parameters
    for param in ["GITHUB_OWNER", "PROJECT_NAME"]:
        current_value = updated.get(param, "")
        if current_value.startswith("{{"):
            current_value = ""
        
        prompt_text = f"{param.replace('_', ' ').title()}"
        if current_value:
            prompt_text += f" [{current_value}]"
        
        user_input = click.prompt(prompt_text, default=current_value, show_default=False)
        if user_input:
            updated[param] = user_input
    
    return updated


def _initialize_acf_state(
    state_manager: StateManager, 
    template_manager: TemplateManager,
    parameters: Dict[str, str]
) -> None:
    """Initialize ACF state file.
    
    Args:
        state_manager: State manager instance
        template_manager: Template manager instance
        parameters: Template parameters used
    """
    # Create .acforge directory
    acf_dir = state_manager.repo_root / ".acforge"
    acf_dir.mkdir(exist_ok=True)
    
    # Build template file information
    template_files = {}
    available_templates = template_manager.list_template_files()
    
    for template_path in available_templates:
        template_info = template_manager.get_template_info(template_path)
        if template_info:
            template_files[template_path] = template_info
    
    # Create initial state
    initial_state = ACForgeState(
        installation=InstallationState(
            template_version=parameters.get("TEMPLATE_VERSION", "unknown"),
            installed_at=datetime.now(),
            cli_version=__version__,
        ),
        templates=TemplateState(
            checksum=template_manager.calculate_bundle_checksum(),
            files=template_files,
        ),
    )
    
    # Save state
    with state_manager.atomic_update() as state:
        state.installation = initial_state.installation
        state.templates = initial_state.templates



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
                param_count = len([v for v in results["parameters_used"].values() if v and not v.startswith("{{")])
                click.echo(f"  ✅ {param_count} parameters substituted")
            
            click.echo()
            
            # Show next steps
            click.echo("💡 Next steps:")
            click.echo("  - Run 'acforge status' to verify configuration")
            click.echo("  - Open repository in Claude Code to test setup")
            click.echo("  - Customize templates by creating .local files")
            click.echo("  - Use 'acforge update' to sync with latest templates")
            
            # Show git rollback instructions if git was used
            if results.get("git_used", False):
                click.echo()
                click.echo("🔄 Git rollback options:")
                if results.get("pre_commit_made", False):
                    click.echo("  - Undo initialization: git reset --hard HEAD~1")
                    click.echo("  - Keep changes but unstage: git reset --soft HEAD~1")
                else:
                    click.echo("  - Undo initialization: git reset --hard HEAD~1")
                click.echo("  - View changes: git log --oneline -3")
            
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