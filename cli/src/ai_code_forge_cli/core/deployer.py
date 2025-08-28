"""Template deployment and parameter substitution utilities."""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from .. import __version__
from .state import ACFState, FileInfo, InstallationState, StateManager, TemplateState
from .templates import TemplateManager


class ParameterSubstitutor:
    """Handles parameter substitution in template content."""
    
    def __init__(self, parameters: Dict[str, str]) -> None:
        """Initialize parameter substitutor.
        
        Args:
            parameters: Dictionary of parameters to substitute
        """
        self.parameters = parameters
        self.substituted = set()
    
    def substitute_content(self, content: str) -> str:
        """Substitute parameters in content.
        
        Args:
            content: Content with {{PARAMETER}} placeholders
            
        Returns:
            Content with parameters substituted
        """
        def replace_parameter(match):
            param_name = match.group(1)
            if param_name in self.parameters:
                self.substituted.add(param_name)
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
        self.claude_dir = target_path / ".claude"
    
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
            # Create .claude directory
            if not dry_run:
                self.claude_dir.mkdir(exist_ok=True)
            results["directories_created"].append(".claude/")
            
            # Get all template files
            template_files = self.template_manager.list_template_files()
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
            template_path: Template file path (e.g., "agents/foundation/context.md")
            
        Returns:
            Target file path in .claude directory
        """
        # Remove .template suffix if present
        clean_path = template_path.replace(".template", "")
        return self.claude_dir / clean_path