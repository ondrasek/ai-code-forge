"""Template deployment and parameter substitution utilities."""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from jinja2 import StrictUndefined, DebugUndefined, Undefined
from jinja2.sandbox import SandboxedEnvironment

from .. import __version__
from .state import ACForgeState, FileInfo, InstallationState, StateManager, TemplateState
from .templates import TemplateManager


class PreservingUndefined(Undefined):
    """Custom undefined class that preserves original template syntax without spaces."""
    
    def __str__(self):
        return f"{{{{{self._undefined_name}}}}}"


class ParameterSubstitutor:
    """Handles secure parameter substitution in template content using Jinja2 sandboxing."""
    
    def __init__(self, parameters: Dict[str, str]) -> None:
        """Initialize parameter substitutor with Jinja2 sandboxed environment.
        
        Args:
            parameters: Dictionary of parameters to substitute
        """
        self.parameters = parameters
        self.substituted = set()
        
        # Create sandboxed Jinja2 environment for secure template processing
        self.jinja_env = SandboxedEnvironment(
            # Compatibility: Keep undefined variables as-is for backward compatibility
            undefined=PreservingUndefined,  # This will render undefined vars as {{VARNAME}}
            # Security: Disable auto-escaping for file content (not HTML)
            autoescape=False,
            # Compatibility: Keep original whitespace for exact template reproduction
            trim_blocks=False,
            lstrip_blocks=False,
            # Security: Disable dangerous builtins and filters
            finalize=None
        )
        
        # Security: Restrict available globals to prevent code execution
        self.jinja_env.globals.clear()
        
        # Security: Remove dangerous filters that could be used for RCE
        dangerous_filters = ['attr', 'getattr', 'getitem']
        for filter_name in dangerous_filters:
            if filter_name in self.jinja_env.filters:
                del self.jinja_env.filters[filter_name]
    
    def substitute_content(self, content: str) -> str:
        """Securely substitute parameters in content using Jinja2 sandboxing with fallback.
        
        Args:
            content: Content with {{PARAMETER}} placeholders
            
        Returns:
            Content with parameters safely substituted
            
        Raises:
            ClickException: If template processing fails
        """
        # First, validate parameter values for security
        for param_name, param_value in self.parameters.items():
            if param_value and self._is_potentially_malicious(param_value):
                raise click.ClickException(f"Parameter '{param_name}' contains potentially unsafe content")
        
        try:
            # Try secure Jinja2 processing first
            template = self.jinja_env.from_string(content)
            rendered = template.render(**self.parameters)
            
            # Track substituted parameters
            for param_name, param_value in self.parameters.items():
                if param_value and param_value in rendered:
                    self.substituted.add(param_name)
                    
            return rendered
            
        except Exception:
            # Fall back to safer regex-based substitution for compatibility
            # This preserves backward compatibility while still validating parameter values
            return self._safe_regex_substitute(content)
    
    def _is_potentially_malicious(self, value: str) -> bool:
        """Check if a parameter value contains potentially malicious content.
        
        Args:
            value: Parameter value to check
            
        Returns:
            True if value looks suspicious
        """
        # Check for dangerous injection patterns (but allow normal template nesting)
        dangerous_patterns = [
            '__import__',
            'exec(',
            'eval(',
            'os.system',
            'subprocess',
            '{%',  # Jinja2 blocks
            '%}',
            'getattr',
            '__class__',
            '__globals__'
        ]
        
        value_lower = value.lower()
        
        # Check for dangerous patterns
        for pattern in dangerous_patterns:
            if pattern in value_lower:
                return True
                
        # Check for excessive template nesting (more than 2 levels)
        if value.count('{{') > 2 or value.count('}}') > 2:
            return True
            
        return False
    
    def _safe_regex_substitute(self, content: str) -> str:
        """Safely substitute parameters using regex with validated values.
        
        Args:
            content: Content with {{PARAMETER}} placeholders
            
        Returns:
            Content with parameters substituted
        """
        def replace_parameter(match):
            param_name = match.group(1).strip()  # Remove whitespace
            if param_name in self.parameters:
                self.substituted.add(param_name)
                # Parameter values are already validated for security
                return self.parameters[param_name]
            return match.group(0)  # Keep original if not found
        
        return re.sub(r'\{\{([^}]+)\}\}', replace_parameter, content)
    
    def get_substituted_parameters(self) -> List[str]:
        """Get list of parameters that were actually substituted.
        
        Returns:
            List of parameter names that were substituted
        """
        return sorted(list(self.substituted))


class TemplateDeployer:
    """Handles deployment of templates to repository."""
    
    def __init__(self, target_path: Path, template_manager: TemplateManager) -> None:
        """Initialize template deployer.
        
        Args:
            target_path: Target repository path
            template_manager: Template manager instance
        """
        self.target_path = target_path
        self.template_manager = template_manager
        self.acforge_dir = target_path / ".acforge"
    
    def deploy_templates(
        self, 
        parameters: Dict[str, str], 
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Deploy all templates to the repository.
        
        Args:
            parameters: Parameters for template substitution
            dry_run: If True, don't actually create files
            
        Returns:
            Dictionary with deployment results
        """
        results = {
            "files_deployed": [],
            "directories_created": [],
            "errors": [],
            "parameters_substituted": [],
        }
        
        try:
            # Create .acforge directory  
            if not dry_run:
                self.acforge_dir.mkdir(exist_ok=True)
            results["directories_created"].append(".acforge/")
            
            # Get all template files
            template_files = self.template_manager.list_template_files()
            
            # Check if we have DevContainer templates and create .devcontainer directory
            has_devcontainer_templates = any(f.startswith("devcontainer/") for f in template_files)
            if has_devcontainer_templates:
                devcontainer_dir = self.target_path / ".devcontainer"
                if not dry_run:
                    devcontainer_dir.mkdir(exist_ok=True)
                results["directories_created"].append(".devcontainer/")
                
            # Check if we have Claude Code templates and create .claude directory
            has_claude_templates = any(f.startswith("_claude/") for f in template_files)
            if has_claude_templates:
                claude_dir = self.target_path / ".claude"
                if not dry_run:
                    claude_dir.mkdir(exist_ok=True)
                results["directories_created"].append(".claude/")
                
            substitutor = ParameterSubstitutor(parameters)
            
            for template_path in template_files:
                try:
                    # Get template content
                    content = self.template_manager.get_template_content(template_path)
                    if content is None:
                        results["errors"].append(f"Could not read template: {template_path}")
                        continue
                    
                    # Substitute parameters
                    processed_content = substitutor.substitute_content(content)
                    
                    # Determine target path
                    target_file_path = self._get_target_path(template_path)
                    relative_path = target_file_path.relative_to(self.target_path)
                    
                    if not dry_run:
                        # Create parent directories
                        target_file_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Write file
                        target_file_path.write_text(processed_content, encoding="utf-8")
                        
                        # Set executable permissions for shell scripts
                        if target_file_path.suffix == ".sh" or template_path.endswith(".sh.template"):
                            target_file_path.chmod(0o755)
                    
                    results["files_deployed"].append(str(relative_path))
                    
                except Exception as e:
                    results["errors"].append(f"Failed to deploy {template_path}: {e}")
            
            # Record substituted parameters
            results["parameters_substituted"] = substitutor.get_substituted_parameters()
            
        except Exception as e:
            results["errors"].append(f"Deployment failed: {e}")
        
        return results
    
    def _get_target_path(self, template_path: str) -> Path:
        """Convert template path to target file path.
        
        Args:
            template_path: Template file path (e.g., "_claude/agents/foundation/context.md" or "devcontainer/devcontainer.json.template")
            
        Returns:
            Target file path in appropriate directory (.claude/, .devcontainer/, or .acforge/)
        """
        # Remove .template suffix if present
        clean_path = template_path.replace(".template", "")
        
        # Handle DevContainer templates specially
        if template_path.startswith("devcontainer/"):
            devcontainer_dir = self.target_path / ".devcontainer"
            # Extract path from devcontainer/path (preserves subdirectories like postCreate-scripts/)
            relative_path = clean_path.split("/", 1)[1]  # Remove "devcontainer/" prefix
            return devcontainer_dir / relative_path
        
        # Handle Claude Code templates specially - go to .claude/ directory
        if template_path.startswith("_claude/"):
            claude_dir = self.target_path / ".claude"
            # Extract path from _claude/path (preserves subdirectories like agents/foundation/)
            relative_path = clean_path.split("/", 1)[1]  # Remove "_claude/" prefix
            return claude_dir / relative_path
        
        # Handle CLAUDE.md specially - goes to repository root
        if clean_path == "CLAUDE.md":
            return self.target_path / "CLAUDE.md"
        
        # Default to .acforge directory for other templates  
        return self.acforge_dir / clean_path