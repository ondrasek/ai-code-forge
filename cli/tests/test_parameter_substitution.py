"""Unit tests for parameter substitution functionality."""

import pytest

from ai_code_forge_cli.core.deployer import ParameterSubstitutor


class TestParameterSubstitutor:
    """Unit tests for ParameterSubstitutor class."""

    def test_basic_parameter_substitution(self):
        """Test basic parameter replacement."""
        substitutor = ParameterSubstitutor({
            "PROJECT_NAME": "test-project",
            "GITHUB_OWNER": "testuser"
        })
        
        content = "Hello {{GITHUB_OWNER}} from {{PROJECT_NAME}}!"
        result = substitutor.substitute_content(content)
        
        assert result == "Hello testuser from test-project!"
        assert set(substitutor.get_substituted_parameters()) == {"GITHUB_OWNER", "PROJECT_NAME"}

    def test_missing_parameters_preserved(self):
        """Test that undefined parameters are left as placeholders."""
        substitutor = ParameterSubstitutor({"DEFINED": "value"})
        
        content = "{{DEFINED}} and {{UNDEFINED}} remain"
        result = substitutor.substitute_content(content)
        
        assert result == "value and {{UNDEFINED}} remain"
        assert substitutor.get_substituted_parameters() == ["DEFINED"]

    def test_empty_parameters_dict(self):
        """Test behavior with no parameters defined."""
        substitutor = ParameterSubstitutor({})
        
        content = "No {{SUBSTITUTION}} happens here"
        result = substitutor.substitute_content(content)
        
        assert result == "No {{SUBSTITUTION}} happens here"
        assert substitutor.get_substituted_parameters() == []

    def test_special_characters_in_values(self):
        """Test parameter values with special characters."""
        substitutor = ParameterSubstitutor({
            "SPECIAL": "user@domain.com",
            "PATH": "/path/with-dashes_and.dots/file",
            "COMPLEX": "value with spaces & symbols!"
        })
        
        content = "Email: {{SPECIAL}}, Path: {{PATH}}, Complex: {{COMPLEX}}"
        result = substitutor.substitute_content(content)
        
        expected = "Email: user@domain.com, Path: /path/with-dashes_and.dots/file, Complex: value with spaces & symbols!"
        assert result == expected

    def test_repeated_parameters(self):
        """Test that same parameter can appear multiple times."""
        substitutor = ParameterSubstitutor({"NAME": "Claude"})
        
        content = "Hello {{NAME}}, how are you {{NAME}}? {{NAME}} is great!"
        result = substitutor.substitute_content(content)
        
        assert result == "Hello Claude, how are you Claude? Claude is great!"
        # Should only record parameter once
        assert substitutor.get_substituted_parameters() == ["NAME"]

    def test_malformed_placeholders_ignored(self):
        """Test that malformed placeholders are left unchanged."""
        substitutor = ParameterSubstitutor({"VALID": "replaced"})
        
        content = "{{VALID}} but {INVALID} and {{ SPACED }} and {{UNCLOSED"
        result = substitutor.substitute_content(content)
        
        assert result == "replaced but {INVALID} and {{ SPACED }} and {{UNCLOSED"
        assert substitutor.get_substituted_parameters() == ["VALID"]

    def test_nested_braces_handling(self):
        """Test handling of nested or adjacent braces."""
        substitutor = ParameterSubstitutor({"PARAM": "value"})
        
        content = "{{{PARAM}}} and {{{{PARAM}}}}"
        result = substitutor.substitute_content(content)
        
        # Current implementation doesn't handle nested braces - they remain unchanged
        # This documents the current behavior
        assert result == "{{{PARAM}}} and {{{{PARAM}}}}"

    def test_case_sensitivity(self):
        """Test that parameter names are case-sensitive."""
        substitutor = ParameterSubstitutor({
            "param": "lowercase",
            "PARAM": "UPPERCASE"
        })
        
        content = "{{param}} vs {{PARAM}} vs {{Param}}"
        result = substitutor.substitute_content(content)
        
        assert result == "lowercase vs UPPERCASE vs {{Param}}"
        assert set(substitutor.get_substituted_parameters()) == {"param", "PARAM"}

    def test_empty_string_parameter_value(self):
        """Test parameter with empty string value."""
        substitutor = ParameterSubstitutor({"EMPTY": ""})
        
        content = "Before{{EMPTY}}After"
        result = substitutor.substitute_content(content)
        
        assert result == "BeforeAfter"
        assert substitutor.get_substituted_parameters() == ["EMPTY"]

    def test_none_parameter_value_substituted(self):
        """Test that None parameter values get substituted as empty string.""" 
        substitutor = ParameterSubstitutor({"NONE_VAL": None})
        
        content = "{{NONE_VAL}} should remain"
        result = substitutor.substitute_content(content)
        
        # Current implementation substitutes None as empty string
        assert result == " should remain"
        assert substitutor.get_substituted_parameters() == ["NONE_VAL"]

    def test_large_content_performance(self):
        """Test substitution performance with large content."""
        substitutor = ParameterSubstitutor({"REPEAT": "X"})
        
        # Create large content with many replacements
        content = "{{REPEAT}}" * 1000 + " some text " + "{{REPEAT}}" * 1000
        result = substitutor.substitute_content(content)
        
        expected = "X" * 1000 + " some text " + "X" * 1000
        assert result == expected
        assert substitutor.get_substituted_parameters() == ["REPEAT"]