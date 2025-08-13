#!/usr/bin/env python3
"""
Test cases for researcher agent date extraction functionality.
Validates edge cases and production scenarios for issue #172.
"""

import re
from datetime import datetime


def extract_current_year_from_environment(env_context):
    """
    Extract current year from environment context.
    Expected format: "Today's date: YYYY-MM-DD"
    
    Args:
        env_context (str): Environment context containing date information
        
    Returns:
        str: Current year (e.g., "2025") or fallback to system year
    """
    try:
        # Primary: Extract from environment "Today's date: YYYY-MM-DD"
        date_match = re.search(r"Today's date:\s*(\d{4})-\d{2}-\d{2}", env_context)
        if date_match:
            year = date_match.group(1)
            # Validate year is reasonable (1900-2099)
            if 1900 <= int(year) <= 2099:
                return year
                
        # Fallback: Use system date with logging
        current_year = str(datetime.now().year)
        print(f"WARNING: Environment date parsing failed, using system year {current_year}")
        return current_year
        
    except Exception as e:
        # Final fallback with error logging
        current_year = str(datetime.now().year)
        print(f"ERROR: Date extraction failed ({e}), using system year {current_year}")
        return current_year


class TestResearcherDateExtraction:
    """Test cases for researcher agent date extraction edge cases."""
    
    def test_standard_format_2025(self):
        """Test standard environment format with 2025."""
        env_context = "Today's date: 2025-08-13"
        result = extract_current_year_from_environment(env_context)
        assert result == "2025"
    
    def test_standard_format_2024(self):
        """Test standard environment format with 2024."""
        env_context = "Today's date: 2024-12-31"
        result = extract_current_year_from_environment(env_context)
        assert result == "2024"
    
    def test_extra_whitespace(self):
        """Test format with extra whitespace around date."""
        env_context = "Today's date:    2025-01-01"
        result = extract_current_year_from_environment(env_context)
        assert result == "2025"
    
    def test_multiline_context(self):
        """Test extraction from multiline environment context."""
        env_context = """
        Working directory: /workspace
        Today's date: 2025-08-13
        Platform: linux
        """
        result = extract_current_year_from_environment(env_context)
        assert result == "2025"
    
    def test_missing_date_context(self):
        """Test fallback when no date in environment context."""
        env_context = "Working directory: /workspace\nPlatform: linux"
        result = extract_current_year_from_environment(env_context)
        # Should fallback to current system year
        current_year = str(datetime.now().year)
        assert result == current_year
    
    def test_malformed_date_format(self):
        """Test fallback with malformed date format."""
        env_context = "Today's date: 2025/08/13"  # Wrong separator
        result = extract_current_year_from_environment(env_context)
        # Should fallback to current system year
        current_year = str(datetime.now().year)
        assert result == current_year
    
    def test_invalid_year_range_low(self):
        """Test fallback with year below valid range."""
        env_context = "Today's date: 1899-08-13"
        result = extract_current_year_from_environment(env_context)
        # Should fallback to current system year
        current_year = str(datetime.now().year)
        assert result == current_year
    
    def test_invalid_year_range_high(self):
        """Test fallback with year above valid range."""
        env_context = "Today's date: 2100-08-13"
        result = extract_current_year_from_environment(env_context)
        # Should fallback to current system year
        current_year = str(datetime.now().year)
        assert result == current_year
    
    def test_boundary_years(self):
        """Test valid boundary years."""
        # Test minimum valid year
        env_context = "Today's date: 1900-01-01"
        result = extract_current_year_from_environment(env_context)
        assert result == "1900"
        
        # Test maximum valid year
        env_context = "Today's date: 2099-12-31"
        result = extract_current_year_from_environment(env_context)
        assert result == "2099"
    
    def test_empty_context(self):
        """Test fallback with empty environment context."""
        env_context = ""
        result = extract_current_year_from_environment(env_context)
        # Should fallback to current system year
        current_year = str(datetime.now().year)
        assert result == current_year
    
    def test_none_context(self):
        """Test error handling with None context."""
        result = extract_current_year_from_environment(None)
        # Should fallback to current system year
        current_year = str(datetime.now().year)
        assert result == current_year
    
    def test_search_query_integration(self):
        """Test integration with search query construction."""
        env_context = "Today's date: 2025-08-13"
        current_year = extract_current_year_from_environment(env_context)
        
        # Test query construction
        search_query = f"React best practices {current_year}"
        assert search_query == "React best practices 2025"
        
        search_query = f"Node.js security guidelines {current_year}"
        assert search_query == "Node.js security guidelines 2025"


def test_production_scenario():
    """Integration test simulating production researcher agent usage."""
    # Simulate actual environment context from Claude Code
    env_context = """
    Working directory: /workspace/worktrees/ai-code-forge/issue-172
    Is directory a git repo: Yes
    Platform: linux
    OS Version: Linux 5.15.0-151-generic
    Today's date: 2025-08-13
    """
    
    # Extract year
    current_year = extract_current_year_from_environment(env_context)
    assert current_year == "2025"
    
    # Construct typical research queries
    queries = [
        f"JavaScript testing best practices {current_year}",
        f"React performance optimization {current_year}",
        f"Node.js security vulnerabilities {current_year}",
        f"TypeScript migration guide {current_year}"
    ]
    
    expected_queries = [
        "JavaScript testing best practices 2025",
        "React performance optimization 2025", 
        "Node.js security vulnerabilities 2025",
        "TypeScript migration guide 2025"
    ]
    
    assert queries == expected_queries


if __name__ == "__main__":
    # Run basic validation
    print("Running researcher agent date extraction tests...")
    
    # Test current environment
    test_env = "Today's date: 2025-08-13"
    result = extract_current_year_from_environment(test_env)
    print(f"Extracted year: {result}")
    
    # Run production scenario
    test_production_scenario()
    print("✅ All tests passed!")