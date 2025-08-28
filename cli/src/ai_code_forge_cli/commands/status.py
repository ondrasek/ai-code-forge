"""Status command implementation."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import click

from ..core.state import StateManager
from ..core.templates import RepositoryAnalyzer, TemplateManager


def _format_datetime(dt: datetime) -> str:
    """Format datetime for human-readable output."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _format_size(size_bytes: int) -> str:
    """Format file size for human-readable output."""
    for unit in ['B', 'KB', 'MB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}GB"


class StatusReporter:
    """Generates status reports in different formats."""
    
    def __init__(self, repo_root: Path, verbose: bool = False) -> None:
        """Initialize status reporter.
        
        Args:
            repo_root: Repository root directory
            verbose: Whether to include verbose output
        """
        self.repo_root = repo_root
        self.verbose = verbose
        self.state_manager = StateManager(repo_root)
        self.template_manager = TemplateManager()
        self.repo_analyzer = RepositoryAnalyzer(repo_root)
    
    def generate_status_data(self) -> Dict[str, Any]:
        """Generate complete status data.
        
        Returns:
            Dictionary with all status information
        """
        # Load current state
        current_state = self.state_manager.load_state()
        state_info = self.state_manager.get_state_info()
        
        # Analyze repository
        repo_info = self.repo_analyzer.get_repository_info()
        existing_files = self.repo_analyzer.get_existing_files()
        customized_files = self.repo_analyzer.find_customized_files()
        
        # Analyze templates
        available_templates = self.template_manager.list_template_files()
        template_errors = self.template_manager.validate_templates()
        bundle_checksum = self.template_manager.calculate_bundle_checksum()
        
        # Compare current vs available templates
        template_comparison = self._compare_templates(current_state, available_templates)
        
        return {
            "repository": repo_info,
            "state": {
                "current": current_state.model_dump(mode="json"),
                "file_info": state_info,
            },
            "templates": {
                "available_count": len(available_templates),
                "available_files": available_templates if self.verbose else [],
                "bundle_checksum": bundle_checksum,
                "validation_errors": template_errors,
            },
            "configuration": {
                "existing_files": list(existing_files),
                "existing_count": len(existing_files),
                "customized_files": customized_files,
                "customized_count": len(customized_files),
            },
            "analysis": template_comparison,
            "timestamp": datetime.now().isoformat(),
        }
    
    def _compare_templates(self, current_state: Any, available_templates: List[str]) -> Dict[str, Any]:
        """Compare current state with available templates.
        
        Args:
            current_state: Current ACF state
            available_templates: List of available template files
            
        Returns:
            Dictionary with comparison analysis
        """
        analysis = {
            "status": "unknown",
            "needs_init": False,
            "needs_update": False,
            "has_conflicts": False,
            "missing_templates": [],
            "outdated_templates": [],
            "extra_files": [],
        }
        
        # Check if ACF has been initialized
        if current_state.installation is None:
            analysis["status"] = "not_initialized"
            analysis["needs_init"] = True
            return analysis
        
        # Get current template state
        current_templates = set(current_state.templates.files.keys()) if current_state.templates else set()
        available_templates_set = set(available_templates)
        existing_files = self.repo_analyzer.get_existing_files()
        
        # Find missing templates (available but not installed)
        missing = available_templates_set - current_templates
        analysis["missing_templates"] = list(missing)
        
        # Find extra files (installed but not available)
        extra = current_templates - available_templates_set
        analysis["extra_files"] = list(extra)
        
        # Check for outdated templates (checksum mismatch)
        outdated = []
        if current_state.templates and current_state.templates.files:
            for template_path in available_templates:
                if template_path in current_state.templates.files:
                    current_info = current_state.templates.files[template_path]
                    available_info = self.template_manager.get_template_info(template_path)
                    
                    if available_info and current_info.checksum != available_info.checksum:
                        outdated.append(template_path)
        
        analysis["outdated_templates"] = outdated
        
        # Determine overall status
        if missing or outdated:
            analysis["status"] = "update_needed"
            analysis["needs_update"] = True
        elif extra:
            analysis["status"] = "has_extra_files"
        else:
            analysis["status"] = "up_to_date"
        
        # Check for conflicts (customized files that would be overwritten)
        customized_files = set(self.repo_analyzer.find_customized_files())
        templates_to_update = missing.union(set(outdated))
        
        # Convert template paths to potential file paths
        potential_conflicts = []
        for template_path in templates_to_update:
            # Check if there's a corresponding .local file
            base_path = template_path.replace("templates/", "").replace(".template", "")
            for existing_file in existing_files:
                if base_path in existing_file and ".local" in existing_file:
                    potential_conflicts.append(existing_file)
        
        analysis["has_conflicts"] = len(potential_conflicts) > 0
        analysis["potential_conflicts"] = potential_conflicts
        
        return analysis
    
    def print_human_readable(self, data: Dict[str, Any]) -> None:
        """Print human-readable status report.
        
        Args:
            data: Status data from generate_status_data()
        """
        click.echo(f"🔍 ACF Status Report - {self.repo_root}")
        click.echo("=" * 50)
        
        # Repository information
        repo = data["repository"]
        click.echo(f"📁 Repository: {repo['config_type']} configuration")
        if repo["is_git_repo"]:
            click.echo("   ✅ Git repository detected")
        else:
            click.echo("   ⚠️  Not a git repository")
        
        # State information
        state_info = data["state"]["file_info"]
        if state_info["state_file_exists"]:
            click.echo(f"📋 State file: {_format_size(state_info['state_file_size'])}")
            if "last_modified" in state_info:
                click.echo(f"   Last modified: {_format_datetime(state_info['last_modified'])}")
        else:
            click.echo("📋 State file: Not found")
        
        # Installation status
        installation = data["state"]["current"]["installation"]
        if installation:
            click.echo(f"⚙️  Installation: {installation['template_version']} (CLI {installation['cli_version']})")
            click.echo(f"   Installed: {installation['installed_at'][:19]}")  # Trim microseconds
        else:
            click.echo("⚙️  Installation: Not initialized")
        
        # Template information
        templates = data["templates"]
        click.echo(f"📦 Templates: {templates['available_count']} files available")
        if templates["validation_errors"]:
            click.echo(f"   ❌ {len(templates['validation_errors'])} validation errors")
            if self.verbose:
                for path, error in templates["validation_errors"].items():
                    click.echo(f"      {path}: {error}")
        else:
            click.echo("   ✅ All templates valid")
        
        # Configuration files
        config = data["configuration"]
        click.echo(f"📄 Configuration: {config['existing_count']} files, {config['customized_count']} customized")
        
        # Analysis results
        analysis = data["analysis"]
        status_icon = {
            "not_initialized": "❌",
            "update_needed": "⚠️ ",
            "up_to_date": "✅",
            "has_extra_files": "ℹ️ ",
            "unknown": "❓"
        }.get(analysis["status"], "❓")
        
        click.echo(f"{status_icon} Status: {analysis['status'].replace('_', ' ').title()}")
        
        # Detailed analysis
        if analysis["needs_init"]:
            click.echo("   💡 Run 'acf init' to initialize ACF configuration")
        
        if analysis["needs_update"]:
            if analysis["missing_templates"]:
                click.echo(f"   📥 {len(analysis['missing_templates'])} new templates available")
                if self.verbose:
                    for template in analysis["missing_templates"][:5]:  # Show first 5
                        click.echo(f"      + {template}")
                    if len(analysis["missing_templates"]) > 5:
                        click.echo(f"      ... and {len(analysis['missing_templates']) - 5} more")
            
            if analysis["outdated_templates"]:
                click.echo(f"   🔄 {len(analysis['outdated_templates'])} templates need updates")
                if self.verbose:
                    for template in analysis["outdated_templates"][:5]:  # Show first 5
                        click.echo(f"      ~ {template}")
                    if len(analysis["outdated_templates"]) > 5:
                        click.echo(f"      ... and {len(analysis['outdated_templates']) - 5} more")
            
            if analysis["has_conflicts"]:
                click.echo(f"   ⚠️  {len(analysis.get('potential_conflicts', []))} potential conflicts with customizations")
            
            click.echo("   💡 Run 'acf update' to sync with latest templates")
        
        if analysis["extra_files"]:
            click.echo(f"   📤 {len(analysis['extra_files'])} extra files not in current templates")
            if self.verbose:
                for extra in analysis["extra_files"][:3]:
                    click.echo(f"      - {extra}")
                if len(analysis["extra_files"]) > 3:
                    click.echo(f"      ... and {len(analysis['extra_files']) - 3} more")


@click.command("status")
@click.option(
    "--format", "output_format",
    type=click.Choice(["human", "json"], case_sensitive=False),
    default="human",
    help="Output format (human-readable or JSON)"
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Show detailed information"
)
@click.pass_obj
def status_command(acf_ctx: Any, output_format: str, verbose: bool) -> None:
    """Show ACF configuration status and template information.
    
    The status command provides comprehensive information about:
    - Repository configuration state (ACF vs Claude vs none)
    - Template availability and validation
    - State file integrity and metadata
    - Customization and conflict analysis
    - Recommendations for next actions
    
    Use --format=json for machine-readable output suitable for scripting.
    """
    try:
        repo_root = acf_ctx.find_repo_root()
        reporter = StatusReporter(repo_root, verbose or acf_ctx.verbose)
        
        status_data = reporter.generate_status_data()
        
        if output_format.lower() == "json":
            click.echo(json.dumps(status_data, indent=2, ensure_ascii=False))
        else:
            reporter.print_human_readable(status_data)
    
    except Exception as e:
        if acf_ctx.verbose:
            raise
        else:
            raise click.ClickException(f"Failed to generate status: {e}")