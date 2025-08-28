"""Repository initialization functionality."""

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import click

from .. import __version__
from .state import ACFState, InstallationState, StateManager
from .templates import TemplateManager


class RepositoryDetector:
    """Detects repository metadata using GitHub CLI."""
    
    def __init__(self, repo_path: Path) -> None:
        """Initialize repository detector.
        
        Args:
            repo_path: Path to repository directory
        """
        self.repo_path = repo_path
    
    def detect_github_info(self) -> Dict[str, Optional[str]]:
        """Detect GitHub repository information using gh CLI.
        
        Returns:
            Dictionary with github_owner, project_name, repo_url
        """
        info = {
            "github_owner": None,
            "project_name": None,
            "repo_url": None,
        }
        
        try:
            # Try gh CLI first for accurate GitHub info
            result = subprocess.run(
                ["gh", "repo", "view", "--json", "owner,name,url"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                info["github_owner"] = data.get("owner", {}).get("login")
                info["project_name"] = data.get("name")  
                info["repo_url"] = data.get("url")
                return info
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError):
            # gh CLI not available or failed, continue with fallbacks
            pass
        
        # Fallback: Try git remote
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                remote_url = result.stdout.strip()
                github_match = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$", remote_url)
                if github_match:
                    info["github_owner"] = github_match.group(1)
                    info["project_name"] = github_match.group(2)
                    info["repo_url"] = f"https://github.com/{github_match.group(1)}/{github_match.group(2)}"
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
        
        # Fallback: Use directory name for project
        if not info["project_name"]:
            info["project_name"] = self.repo_path.name
        
        return info
    
    def is_git_repository(self) -> bool:
        """Check if directory is a git repository."""
        return (self.repo_path / ".git").exists()
    
    def check_existing_configuration(self) -> Dict[str, bool]:
        """Check for existing ACF/Claude configuration.
        
        Returns:
            Dictionary with has_acf, has_claude flags
        """
        return {
            "has_acf": (self.repo_path / ".acf").exists(),
            "has_claude": (self.repo_path / ".claude").exists(),
        }


class ParameterSubstitutor:
    """Handles template parameter substitution."""
    
    def __init__(self, parameters: Dict[str, str]) -> None:
        """Initialize parameter substitutor.
        
        Args:
            parameters: Dictionary of parameter names to values
        """
        self.parameters = parameters
        self.substituted_params: Set[str] = set()
    
    def substitute_content(self, content: str) -> str:
        """Substitute parameters in template content.
        
        Args:
            content: Template content with {{PARAMETER}} placeholders
            
        Returns:
            Content with parameters substituted
        """
        result = content
        
        # Find all {{PARAMETER}} patterns
        for match in re.finditer(r"\{\{([A-Z_]+)\}\}", content):
            param_name = match.group(1)
            if param_name in self.parameters:
                placeholder = match.group(0)  # Full {{PARAMETER}}
                value = self.parameters[param_name]
                result = result.replace(placeholder, value)
                self.substituted_params.add(param_name)
        
        return result
    
    def get_substituted_parameters(self) -> List[str]:
        """Get list of parameters that were substituted."""
        return sorted(list(self.substituted_params))


class TemplateDeployer:
    """Deploys templates to target directories."""
    
    def __init__(self, target_path: Path, template_manager: TemplateManager) -> None:
        """Initialize template deployer.
        
        Args:
            target_path: Target repository path
            template_manager: Template manager instance
        """
        self.target_path = target_path
        self.template_manager = template_manager
        self.deployed_files: List[str] = []
    
    def deploy_templates(self, parameters: Dict[str, str], dry_run: bool = False) -> Dict[str, Any]:
        """Deploy templates with parameter substitution.
        
        Args:
            parameters: Parameters for template substitution
            dry_run: If True, don't actually write files
            
        Returns:
            Dictionary with deployment results
        """
        substitutor = ParameterSubstitutor(parameters)
        claude_dir = self.target_path / ".claude"
        
        results = {
            "files_deployed": [],
            "files_skipped": [],
            "parameters_substituted": [],
            "errors": [],
        }
        
        # Create .claude directory structure
        if not dry_run:
            claude_dir.mkdir(exist_ok=True)
            (claude_dir / "agents" / "foundation").mkdir(parents=True, exist_ok=True)
            (claude_dir / "agents" / "specialists").mkdir(parents=True, exist_ok=True)
            (claude_dir / "commands").mkdir(parents=True, exist_ok=True)
        
        # Deploy template files
        template_files = self.template_manager.list_template_files()
        
        for template_path in template_files:
            try:
                content = self.template_manager.get_template_content(template_path)
                if content is None:
                    results["errors"].append(f"Could not read template: {template_path}")
                    continue
                
                # Substitute parameters
                processed_content = substitutor.substitute_content(content)
                
                # Determine target file path
                target_file = self._map_template_to_target(template_path, claude_dir)
                
                if not dry_run:
                    # Ensure parent directory exists
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Write processed content
                    target_file.write_text(processed_content, encoding="utf-8")
                
                results["files_deployed"].append(str(target_file.relative_to(self.target_path)))
                self.deployed_files.append(template_path)
                
            except Exception as e:
                results["errors"].append(f"Error deploying {template_path}: {e}")
        
        results["parameters_substituted"] = substitutor.get_substituted_parameters()
        return results
    
    def _map_template_to_target(self, template_path: str, claude_dir: Path) -> Path:
        """Map template path to target file path.
        
        Args:
            template_path: Relative path in templates
            claude_dir: Target .claude directory
            
        Returns:
            Target file path
        """
        # Remove .template suffix if present
        target_name = template_path
        if target_name.endswith('.template'):
            target_name = target_name[:-9]  # Remove .template
        
        # Map specific templates
        if template_path == "CLAUDE.md.template":
            return claude_dir / "CLAUDE.md"
        
        # Default mapping - preserve directory structure
        return claude_dir / target_name


class InitCommand:
    """Implements the acf init command."""
    
    def __init__(self, target_path: Path) -> None:
        """Initialize init command.
        
        Args:
            target_path: Target repository path
        """
        self.target_path = target_path
        self.detector = RepositoryDetector(target_path)
        self.template_manager = TemplateManager()
        self.state_manager = StateManager(target_path)
    
    def run(
        self,
        force: bool = False,
        dry_run: bool = False,
        interactive: bool = False,
        github_owner: Optional[str] = None,
        project_name: Optional[str] = None,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """Execute the init command.
        
        Args:
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
            if not self.target_path.exists():
                results["errors"].append(f"Target directory does not exist: {self.target_path}")
                return results
            
            if not self.target_path.is_dir():
                results["errors"].append(f"Target is not a directory: {self.target_path}")
                return results
            
            # Check existing configuration
            existing_config = self.detector.check_existing_configuration()
            if (existing_config["has_acf"] or existing_config["has_claude"]) and not force:
                if existing_config["has_acf"] and existing_config["has_claude"]:
                    config_type = "ACF and Claude"
                elif existing_config["has_acf"]:
                    config_type = "ACF"
                else:
                    config_type = "Claude"
                
                results["errors"].append(f"{config_type} configuration already exists. Use --force to overwrite.")
                return results
            
            # Detect repository information
            repo_info = self.detector.detect_github_info()
            
            # Override with user-provided values
            if github_owner:
                repo_info["github_owner"] = github_owner
            if project_name:
                repo_info["project_name"] = project_name
            
            # Interactive prompts if requested
            if interactive:
                repo_info = self._interactive_prompts(repo_info)
            
            # Prepare template parameters
            parameters = self._prepare_parameters(repo_info)
            results["parameters_used"] = parameters
            
            if verbose:
                click.echo(f"📋 Using parameters: {parameters}")
            
            # Create .acf directory
            acf_dir = self.target_path / ".acf"
            if not dry_run:
                acf_dir.mkdir(exist_ok=True)
                results["files_created"].append(".acf/")
            
            # Deploy templates
            deployer = TemplateDeployer(self.target_path, self.template_manager)
            deploy_results = deployer.deploy_templates(parameters, dry_run)
            
            results["files_created"].extend(deploy_results["files_deployed"])
            results["errors"].extend(deploy_results["errors"])
            
            if deploy_results["errors"]:
                results["message"] = f"Initialization completed with {len(deploy_results['errors'])} errors"
                results["warnings"].extend(deploy_results["errors"])
            
            # Initialize state
            if not dry_run:
                self._initialize_state(repo_info, deploy_results, deployer.deployed_files)
                results["files_created"].append(".acf/state.json")
            
            results["success"] = True
            if not results["message"]:
                results["message"] = "Repository initialized successfully"
            
        except Exception as e:
            results["errors"].append(f"Initialization failed: {e}")
            results["message"] = f"Failed to initialize repository: {e}"
        
        return results
    
    def _interactive_prompts(self, repo_info: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
        """Prompt user for repository information interactively.
        
        Args:
            repo_info: Detected repository information
            
        Returns:
            Updated repository information
        """
        if not repo_info.get("github_owner"):
            owner = click.prompt("GitHub owner/organization", default="", type=str)
            if owner:
                repo_info["github_owner"] = owner
        
        if not repo_info.get("project_name"):
            name = click.prompt("Project name", default=self.target_path.name, type=str)
            repo_info["project_name"] = name
        
        return repo_info
    
    def _prepare_parameters(self, repo_info: Dict[str, Optional[str]]) -> Dict[str, str]:
        """Prepare template substitution parameters.
        
        Args:
            repo_info: Repository information
            
        Returns:
            Template parameters dictionary
        """
        creation_date = datetime.now().isoformat()
        
        parameters = {
            "GITHUB_OWNER": repo_info.get("github_owner") or "unknown",
            "PROJECT_NAME": repo_info.get("project_name") or "unknown", 
            "REPO_URL": repo_info.get("repo_url") or "{{REPO_URL}}",
            "CREATION_DATE": creation_date,
            "ACF_VERSION": __version__,
            "TEMPLATE_VERSION": self.template_manager.calculate_bundle_checksum()[:8],
        }
        
        return parameters
    
    def _initialize_state(self, repo_info: Dict[str, Optional[str]], deploy_results: Dict[str, Any], deployed_files: List[str]) -> None:
        """Initialize ACF state after successful deployment.
        
        Args:
            repo_info: Repository information
            deploy_results: Template deployment results
            deployed_files: List of deployed template files
        """
        # Create installation state
        installation = InstallationState(
            template_version=self.template_manager.calculate_bundle_checksum()[:8],
            installed_at=datetime.now(),
            cli_version=__version__
        )
        
        # Create template state
        template_checksum = self.template_manager.calculate_bundle_checksum()
        template_files = {}
        
        for template_path in deployed_files:
            template_info = self.template_manager.get_template_info(template_path)
            if template_info:
                template_files[template_path] = template_info
        
        # Create complete state
        state = ACFState(
            installation=installation,
            templates={
                "checksum": template_checksum,
                "files": template_files
            }
        )
        
        # Save state
        self.state_manager.save_state(state)