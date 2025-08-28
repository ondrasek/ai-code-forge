"""Init command implementation."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import click

from .. import __version__
from ..core.detector import RepositoryDetector
from ..core.deployer import TemplateDeployer
from ..core.state import ACFState, FileInfo, InstallationState, StateManager, TemplateState
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
        
        # Execute initialization
        results = _run_init(
            target_path=target_path,
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


def _run_init(
    target_path: Path,
    force: bool = False,
    dry_run: bool = False,
    interactive: bool = False,
    github_owner: Optional[str] = None,
    project_name: Optional[str] = None,
    verbose: bool = False,
) -> Dict[str, Any]:
    """Execute the init command logic.
    
    Args:
        target_path: Target repository path
        force: Overwrite existing configuration
        dry_run: Show what would be done without changes
        interactive: Prompt for parameters
        github_owner: Override GitHub owner detection
        project_name: Override project name detection
        verbose: Show detailed output
        
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
    }
    
    try:
        # Validate target directory
        if not target_path.exists():
            results["errors"].append(f"Target directory does not exist: {target_path}")
            return results
        
        # Initialize components
        detector = RepositoryDetector(target_path)
        template_manager = TemplateManager()
        state_manager = StateManager(target_path)
        
        # Check existing configuration
        existing_config = detector.check_existing_configuration()
        
        if not force and (existing_config["has_acf"] or existing_config["has_claude"]):
            error_msg = "Repository already has ACF or Claude Code configuration. Use --force to overwrite."
            results["errors"].append(error_msg)
            return results
        
        # Detect repository information
        repo_info = detector.detect_github_info()
        
        # Override with explicit parameters
        if github_owner:
            repo_info["github_owner"] = github_owner
        if project_name:
            repo_info["project_name"] = project_name
        
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
        
        # Deploy templates
        deployer = TemplateDeployer(target_path, template_manager)
        deploy_results = deployer.deploy_templates(parameters, dry_run)
        
        results["files_created"] = deploy_results["files_deployed"] + deploy_results["directories_created"]
        results["errors"].extend(deploy_results["errors"])
        
        # Initialize ACF state (if not dry run)
        if not dry_run and not results["errors"]:
            _initialize_acf_state(state_manager, template_manager, parameters)
            results["files_created"].append(".acf/state.json")
        
        if not results["errors"]:
            results["success"] = True
            if dry_run:
                results["message"] = f"Would create {len(results['files_created'])} files"
            else:
                results["message"] = "Repository initialized successfully"
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
    # Create .acf directory
    acf_dir = state_manager.repo_root / ".acf"
    acf_dir.mkdir(exist_ok=True)
    
    # Build template file information
    template_files = {}
    available_templates = template_manager.list_template_files()
    
    for template_path in available_templates:
        template_info = template_manager.get_template_info(template_path)
        if template_info:
            template_files[template_path] = template_info
    
    # Create initial state
    initial_state = ACFState(
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