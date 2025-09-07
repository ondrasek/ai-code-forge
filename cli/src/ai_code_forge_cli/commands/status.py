"""Status command implementation."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import click

from ..core.detector import RepositoryDetector
from ..core.git_wrapper import create_git_wrapper
from ..core.state import StateManager
from ..core.static import StaticContentManager
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
        self.repo_detector = RepositoryDetector(repo_root)
        self.static_manager = StaticContentManager()
    
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
        
        # Analyze static content
        static_files = self.static_manager.list_static_files()
        static_analysis = self._analyze_static_content()
        
        # Detect repository information (GitHub integration)
        github_info = self.repo_detector.detect_github_info()
        existing_config = self.repo_detector.check_existing_configuration()
        
        # Analyze git status if available
        git_analysis = self._analyze_git_status()
        
        # Compare current vs available templates
        template_comparison = self._compare_templates(current_state, available_templates)
        
        return {
            "repository": repo_info,
            "github": {
                "detected": github_info,
                "has_remote": github_info.get("repo_url") is not None,
                "owner": github_info.get("github_owner"),
                "name": github_info.get("project_name"),
            },
            "git": git_analysis,
            "state": {
                "current": current_state.model_dump(mode="json"),
                "file_info": state_info,
                "configuration_type": existing_config,
            },
            "templates": {
                "available_count": len(available_templates),
                "available_files": available_templates if self.verbose else [],
                "bundle_checksum": bundle_checksum,
                "validation_errors": template_errors,
                "claude_templates": len([t for t in available_templates if t.startswith("_claude/")]),
                "devcontainer_templates": len([t for t in available_templates if t.startswith("devcontainer/")]),
            },
            "static_content": {
                "available_count": len(static_files),
                "available_files": static_files if self.verbose else [],
                "analysis": static_analysis,
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
    
    def _analyze_static_content(self) -> Dict[str, Any]:
        """Analyze static content availability and structure."""
        try:
            static_files = self.static_manager.list_static_files()
            
            analysis = {
                "available": len(static_files) > 0,
                "file_count": len(static_files),
                "categories": {
                    "mcp_servers": len([f for f in static_files if f.startswith("mcp-servers/")]),
                    "scripts": len([f for f in static_files if f.startswith("scripts/")]),
                    "tests": len([f for f in static_files if "test" in f.lower()]),
                },
                "errors": [],
            }
            
            # Basic validation - check if key files exist
            key_files = ["mcp-servers/", "scripts/"]
            missing_categories = []
            for key_file in key_files:
                if not any(f.startswith(key_file) for f in static_files):
                    missing_categories.append(key_file)
            
            if missing_categories:
                analysis["errors"].append(f"Missing static content categories: {missing_categories}")
            
            return analysis
            
        except Exception as e:
            return {
                "available": False,
                "file_count": 0,
                "categories": {},
                "errors": [f"Failed to analyze static content: {e}"],
            }
    
    def _analyze_git_status(self) -> Dict[str, Any]:
        """Analyze git repository status."""
        git_analysis = {
            "available": False,
            "branch": None,
            "has_changes": False,
            "behind_remote": False,
            "can_commit": True,
            "status": "unknown",
            "errors": [],
        }
        
        try:
            # Check if we're in a git repository
            if not (self.repo_root / ".git").exists():
                git_analysis["status"] = "not_git_repo"
                return git_analysis
            
            git_analysis["available"] = True
            
            # Try to create git wrapper for detailed analysis
            try:
                # We need a minimal context object for git wrapper
                class MinimalContext:
                    def __init__(self, repo_root):
                        self.repo_root = repo_root
                        self.verbose = False
                
                minimal_ctx = MinimalContext(self.repo_root)
                git_wrapper = create_git_wrapper(minimal_ctx, False)
                
                # Get current version as a proxy for git functionality
                current_version = git_wrapper.get_current_version()
                git_analysis["acf_version_detected"] = current_version is not None
                git_analysis["status"] = "functional"
                
            except Exception as e:
                git_analysis["errors"].append(f"Git wrapper failed: {e}")
                git_analysis["status"] = "limited_functionality"
                
        except Exception as e:
            git_analysis["errors"].append(f"Git analysis failed: {e}")
            git_analysis["status"] = "error"
        
        return git_analysis
    
    def print_human_readable(self, data: Dict[str, Any]) -> None:
        """Print human-readable status report.
        
        Args:
            data: Status data from generate_status_data()
        """
        click.echo(f"🔍 ACF Status Report - {self.repo_root}")
        click.echo("=" * 50)
        
        # Repository information
        repo = data["repository"]
        github = data["github"]
        git = data["git"]
        
        click.echo(f"📁 Repository: {repo['config_type']} configuration")
        
        # Git status
        if git["available"]:
            status_icon = "✅" if git["status"] == "functional" else "⚠️ "
            click.echo(f"   {status_icon} Git: {git['status'].replace('_', ' ')}")
            if git["errors"] and self.verbose:
                for error in git["errors"][:2]:  # Show first 2 errors
                    click.echo(f"      ⚠️  {error}")
        else:
            click.echo("   ❌ Git: Not a git repository")
        
        # GitHub integration
        if github["has_remote"]:
            click.echo(f"   🔗 GitHub: {github['owner']}/{github['name']}")
        elif github["detected"]["github_owner"]:
            click.echo(f"   🔗 GitHub: {github['detected']['github_owner']} (partial detection)")
        else:
            click.echo("   ⚠️  GitHub: No remote detected")
        
        # State information
        state_info = data["state"]["file_info"]
        if state_info["state_file_exists"]:
            click.echo(f"📋 State file: {_format_size(state_info['state_file_size'])}")
            if "last_modified" in state_info:
                # last_modified is now an ISO format string, parse it for formatting
                try:
                    dt = datetime.fromisoformat(state_info['last_modified'])
                    click.echo(f"   Last modified: {_format_datetime(dt)}")
                except (ValueError, TypeError):
                    # Fallback if ISO parsing fails
                    click.echo(f"   Last modified: {state_info['last_modified']}")
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
        if self.verbose:
            click.echo(f"   📋 Claude Code: {templates['claude_templates']} files")
            click.echo(f"   🐳 DevContainer: {templates['devcontainer_templates']} files")
        
        if templates["validation_errors"]:
            click.echo(f"   ❌ {len(templates['validation_errors'])} validation errors")
            if self.verbose:
                for path, error in templates["validation_errors"].items():
                    click.echo(f"      {path}: {error}")
        else:
            click.echo("   ✅ All templates valid")
        
        # Static content information
        static = data["static_content"]
        click.echo(f"📦 Static Content: {static['available_count']} files available")
        if static["analysis"]["available"]:
            if self.verbose:
                categories = static["analysis"]["categories"]
                click.echo(f"   🤖 MCP Servers: {categories.get('mcp_servers', 0)} files")
                click.echo(f"   📜 Scripts: {categories.get('scripts', 0)} files") 
                click.echo(f"   🧪 Tests: {categories.get('tests', 0)} files")
            
            if static["analysis"]["errors"]:
                click.echo(f"   ⚠️  {len(static['analysis']['errors'])} issues detected")
                if self.verbose:
                    for error in static["analysis"]["errors"]:
                        click.echo(f"      ⚠️  {error}")
            else:
                click.echo("   ✅ Static content structure valid")
        else:
            click.echo("   ❌ No static content available")
        
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
            click.echo("   💡 Run 'acforge init' to initialize ACForge configuration")
        
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
            
            click.echo("   💡 Run 'acforge update' to sync with latest templates")
        
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
def status_command(acforge_ctx: Any, output_format: str, verbose: bool) -> None:
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
        repo_root = acforge_ctx.find_repo_root()
        reporter = StatusReporter(repo_root, verbose or acforge_ctx.verbose)
        
        status_data = reporter.generate_status_data()
        
        if output_format.lower() == "json":
            click.echo(json.dumps(status_data, indent=2, ensure_ascii=False))
        else:
            reporter.print_human_readable(status_data)
    
    except Exception as e:
        if acforge_ctx.verbose:
            raise
        else:
            raise click.ClickException(f"Failed to generate status: {e}")