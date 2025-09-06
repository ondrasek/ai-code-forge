"""Unit tests for parameter substitution functionality - focused on real scenarios."""

import pytest

from ai_code_forge_cli.core.deployer import ParameterSubstitutor


class TestParameterSubstitution:
    """Focused tests for meaningful parameter substitution scenarios."""

    def test_real_template_substitution(self):
        """Test substitution with realistic template content."""
        substitutor = ParameterSubstitutor({
            "PROJECT_NAME": "my-project",
            "GITHUB_OWNER": "testuser",
            "CLI_DIRECTORY": "cli"
        })
        
        # Realistic template content similar to actual CLAUDE.md
        content = """<cli>{{CLI_DIRECTORY}}/ with source code for the {{PROJECT_NAME}} cli tool</cli>
<github_issues>GitHub Issues in {{GITHUB_OWNER}}/{{GITHUB_REPO}} (specifications managed via GitHub)</github_issues>"""
        
        result = substitutor.substitute_content(content)
        
        # Verify actual substitutions happened correctly
        assert "cli/ with source code for the my-project cli tool" in result
        assert "GitHub Issues in testuser/{{GITHUB_REPO}}" in result  # Undefined param preserved
        
        # Verify tracking works
        substituted = substitutor.get_substituted_parameters()
        assert set(substituted) == {"PROJECT_NAME", "GITHUB_OWNER", "CLI_DIRECTORY"}

    def test_parameter_security_validation(self):
        """Test that parameter values don't break template structure."""
        # Test potentially dangerous parameter values
        substitutor = ParameterSubstitutor({
            "PROJECT_NAME": "project}}{{malicious",  # Nested braces
            "GITHUB_OWNER": "user@domain.com",      # Special chars
            "PATH_PARAM": "/path/with spaces/file"   # Spaces
        })
        
        content = "Project: {{PROJECT_NAME}}, Owner: {{GITHUB_OWNER}}, Path: {{PATH_PARAM}}"
        result = substitutor.substitute_content(content)
        
        # Verify substitution doesn't break parsing
        assert "project}}{{malicious" in result
        assert "user@domain.com" in result  
        assert "/path/with spaces/file" in result
        
        # Verify all parameters were processed
        assert len(substitutor.get_substituted_parameters()) == 3

    def test_missing_parameters_preserved(self):
        """Test that undefined parameters are preserved for manual handling."""
        substitutor = ParameterSubstitutor({"DEFINED": "value"})
        
        content = "{{DEFINED}} parameter works, {{UNDEFINED}} stays as placeholder"
        result = substitutor.substitute_content(content)
        
        assert result == "value parameter works, {{UNDEFINED}} stays as placeholder"
        assert substitutor.get_substituted_parameters() == ["DEFINED"]