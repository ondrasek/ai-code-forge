"""Tests for Codex integration tools in the OpenAI Structured MCP server."""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, ANY
from openai_structured_mcp.server import (
    codex_generate,
    codex_review,
    codex_refactor,
    codex_explain
)


class TestCodexGenerate:
    """Test cases for codex_generate tool."""
    
    @pytest.mark.asyncio
    @patch('openai.AsyncOpenAI')
    @patch('openai_structured_mcp.server.os.getenv')
    async def test_codex_generate_success(self, mock_getenv, mock_openai_class):
        """Test successful code generation."""
        # Mock environment variables
        mock_getenv.side_effect = lambda key, default=None: {
            'OPENAI_API_KEY': 'test-api-key',
            'OPENAI_DEFAULT_MODEL': 'gpt-5'
        }.get(key, default)
        
        # Mock OpenAI client
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        
        # Mock response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = """
```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

This is a simple recursive implementation of the Fibonacci sequence with proper base cases.
"""
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        # Test the function
        result = await codex_generate.fn(
            prompt="Generate a Fibonacci function",
            language="python",
            style="clean"
        )
        
        # Verify the result
        assert "fibonacci" in result.lower()
        assert "python" in result
        assert "def fibonacci" in result
        
        # Verify OpenAI API was called correctly
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]['model'] == 'gpt-5'
        assert call_args[1]['temperature'] == 0.2
        assert call_args[1]['max_tokens'] == 2000
        assert len(call_args[1]['messages']) == 2
        assert "OpenAI Codex" in call_args[1]['messages'][0]['content']
        assert "Fibonacci" in call_args[1]['messages'][1]['content']
    
    @pytest.mark.asyncio
    @patch('openai_structured_mcp.server.os.getenv')
    async def test_codex_generate_missing_api_key(self, mock_getenv):
        """Test error handling when API key is missing."""
        mock_getenv.return_value = None
        
        result = await codex_generate.fn(prompt="test prompt")
        
        assert "Error: OPENAI_API_KEY environment variable not set" in result
    
    @pytest.mark.asyncio
    @patch('openai.AsyncOpenAI')
    @patch('openai_structured_mcp.server.os.getenv')
    async def test_codex_generate_with_context(self, mock_getenv, mock_openai_class):
        """Test code generation with existing context."""
        mock_getenv.side_effect = lambda key, default=None: {
            'OPENAI_API_KEY': 'test-key'
        }.get(key, default)
        
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Generated code with context"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        result = await codex_generate.fn(
            prompt="Add error handling",
            context="def process_data(data): return data.upper()",
            language="python"
        )
        
        # Verify context was included in the prompt
        call_args = mock_client.chat.completions.create.call_args
        user_message = call_args[1]['messages'][1]['content']
        assert "context to build upon" in user_message.lower()
        assert "def process_data" in user_message


class TestCodexReview:
    """Test cases for codex_review tool."""
    
    @pytest.mark.asyncio
    @patch('openai.AsyncOpenAI')
    @patch('openai_structured_mcp.server.os.getenv')
    async def test_codex_review_success(self, mock_getenv, mock_openai_class):
        """Test successful code review."""
        mock_getenv.side_effect = lambda key, default=None: {
            'OPENAI_API_KEY': 'test-key',
            'OPENAI_DEFAULT_MODEL': 'gpt-5'
        }.get(key, default)
        
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices[0].message.content = """
**Code Review Results**

1. Overall Assessment: 7/10
2. Strengths: Clear function naming, proper type hints
3. Issues Found: 
   - Medium: Missing error handling for edge cases
   - Low: Could benefit from docstring
4. Security Concerns: None identified
5. Performance: Acceptable for expected usage
6. Maintainability: Good structure, easy to understand
7. Recommendations: Add input validation and documentation
8. Code Quality Score: 7/10
"""
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        code_sample = """
def calculate_average(numbers):
    return sum(numbers) / len(numbers)
"""
        
        result = await codex_review.fn(
            code=code_sample,
            language_hint="python",
            focus="comprehensive"
        )
        
        assert "Overall Assessment" in result
        assert "7/10" in result
        assert "Recommendations" in result
        
        # Verify API call parameters
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]['temperature'] == 0.3
        assert call_args[1]['max_tokens'] == 1500
        system_msg = call_args[1]['messages'][0]['content']
        assert "comprehensive" in system_msg
    
    @pytest.mark.asyncio
    @patch('openai.AsyncOpenAI')
    @patch('openai_structured_mcp.server.os.getenv')
    async def test_codex_review_focus_security(self, mock_getenv, mock_openai_class):
        """Test code review with security focus."""
        mock_getenv.side_effect = lambda key, default=None: {'OPENAI_API_KEY': 'test-key'}.get(key, default)
        
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Security-focused review results"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        await codex_review.fn(code="test code", focus="security")
        
        call_args = mock_client.chat.completions.create.call_args
        system_msg = call_args[1]['messages'][0]['content']
        assert "focus on: security" in system_msg


class TestCodexRefactor:
    """Test cases for codex_refactor tool."""
    
    @pytest.mark.asyncio
    @patch('openai.AsyncOpenAI')
    @patch('openai_structured_mcp.server.os.getenv')
    async def test_codex_refactor_preserve_behavior(self, mock_getenv, mock_openai_class):
        """Test refactoring with behavior preservation."""
        mock_getenv.side_effect = lambda key, default=None: {'OPENAI_API_KEY': 'test-key'}.get(key, default)
        
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices[0].message.content = """
**Refactored Code:**

```python
def calculate_average(numbers: List[float]) -> float:
    \"\"\"Calculate the average of a list of numbers.
    
    Args:
        numbers: List of numeric values
        
    Returns:
        Average value as float
        
    Raises:
        ValueError: If list is empty or contains non-numeric values
    \"\"\"
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)
```

**Changes Made:**
- Added type hints for better code clarity
- Added comprehensive docstring
- Added error handling for empty list
- Improved parameter validation

**Improvements:**
- Better error handling prevents runtime crashes
- Type hints improve IDE support and catch errors early  
- Documentation makes function purpose clear
"""
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        original_code = "def calculate_average(numbers): return sum(numbers) / len(numbers)"
        
        result = await codex_refactor.fn(
            code=original_code,
            requirements="Add type hints, error handling, and documentation",
            preserve_behavior=True
        )
        
        assert "Refactored Code" in result
        assert "List[float]" in result
        assert "ValueError" in result
        assert "Changes Made" in result
        
        # Verify API parameters
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]['temperature'] == 0.1  # Low temperature for consistency
        assert call_args[1]['max_tokens'] == 2500
        system_msg = call_args[1]['messages'][0]['content']
        assert "Preserve exact behavior" in system_msg
    
    @pytest.mark.asyncio
    @patch('openai.AsyncOpenAI')
    @patch('openai_structured_mcp.server.os.getenv')
    async def test_codex_refactor_allow_behavior_changes(self, mock_getenv, mock_openai_class):
        """Test refactoring allowing behavior changes."""
        mock_getenv.side_effect = lambda key, default=None: {'OPENAI_API_KEY': 'test-key'}.get(key, default)
        
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Refactored with behavior changes"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        await codex_refactor.fn(
            code="old code",
            requirements="modernize and optimize",
            preserve_behavior=False
        )
        
        call_args = mock_client.chat.completions.create.call_args
        system_msg = call_args[1]['messages'][0]['content']
        assert "Improve behavior while meeting new requirements" in system_msg


class TestCodexExplain:
    """Test cases for codex_explain tool."""
    
    @pytest.mark.asyncio
    @patch('openai.AsyncOpenAI')
    @patch('openai_structured_mcp.server.os.getenv')
    async def test_codex_explain_detailed_developer(self, mock_getenv, mock_openai_class):
        """Test detailed code explanation for developers."""
        mock_getenv.side_effect = lambda key, default=None: {'OPENAI_API_KEY': 'test-key'}.get(key, default)
        
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices[0].message.content = """
**Code Explanation - Detailed Level for Developers**

**High-level Purpose:**
This function implements a recursive algorithm to calculate Fibonacci numbers.

**Key Algorithm Pattern:**
Uses classical recursive approach with base cases for n <= 1.

**Data Flow:**
1. Input validation through base case checking
2. Recursive calls build up call stack
3. Results bubble up through return statements

**Implementation Details:**
- Base cases prevent infinite recursion
- Each call spawns two additional calls (exponential complexity)
- No memoization leads to redundant calculations

**Performance Considerations:**
- Time complexity: O(2^n) - exponential growth
- Space complexity: O(n) - maximum call stack depth
- Inefficient for large inputs due to repeated calculations

**Potential Issues:**
- Stack overflow for large n values (typically n > 1000)
- Exponential time complexity makes it impractical for n > 40
- No input validation for negative numbers or non-integers
"""
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        code_sample = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        
        result = await codex_explain.fn(
            code=code_sample,
            language_hint="python",
            level="detailed",
            audience="developer"
        )
        
        assert "High-level Purpose" in result
        assert "recursive algorithm" in result
        assert "Performance Considerations" in result
        assert "O(2^n)" in result
        
        # Verify API parameters
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]['temperature'] == 0.4
        assert call_args[1]['max_tokens'] == 2000
        system_msg = call_args[1]['messages'][0]['content']
        assert "developer at detailed level" in system_msg
    
    @pytest.mark.asyncio
    @patch('openai.AsyncOpenAI')
    @patch('openai_structured_mcp.server.os.getenv')
    async def test_codex_explain_beginner_student(self, mock_getenv, mock_openai_class):
        """Test beginner-level explanation for students."""
        mock_getenv.side_effect = lambda key, default=None: {'OPENAI_API_KEY': 'test-key'}.get(key, default)
        
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Beginner-friendly explanation"
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        await codex_explain.fn(
            code="simple code",
            level="beginner",
            audience="student"
        )
        
        call_args = mock_client.chat.completions.create.call_args
        system_msg = call_args[1]['messages'][0]['content']
        assert "student at beginner level" in system_msg
        assert "learning programming" in system_msg
        assert "Step-by-step explanation" in system_msg


class TestCodexToolsErrorHandling:
    """Test error handling across all Codex tools."""
    
    @pytest.mark.asyncio
    @patch('openai.AsyncOpenAI')
    @patch('openai_structured_mcp.server.os.getenv')
    async def test_openai_api_exception_handling(self, mock_getenv, mock_openai_class):
        """Test handling of OpenAI API exceptions."""
        mock_getenv.side_effect = lambda key, default=None: {'OPENAI_API_KEY': 'test-key'}.get(key, default)
        
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        # Test all Codex tools handle exceptions gracefully
        tools_and_params = [
            (codex_generate, {"prompt": "test"}),
            (codex_review, {"code": "test code"}),
            (codex_refactor, {"code": "test", "requirements": "improve"}),
            (codex_explain, {"code": "test code"})
        ]
        
        for tool_func, params in tools_and_params:
            result = await tool_func.fn(**params)
            assert "Error during" in result
            assert "API Error" in result
    
    @pytest.mark.asyncio
    @patch('openai_structured_mcp.server.os.getenv')
    async def test_missing_api_key_all_tools(self, mock_getenv):
        """Test all Codex tools handle missing API key."""
        mock_getenv.return_value = None
        
        tools_and_params = [
            (codex_generate, {"prompt": "test"}),
            (codex_review, {"code": "test code"}),
            (codex_refactor, {"code": "test", "requirements": "improve"}),
            (codex_explain, {"code": "test code"})
        ]
        
        for tool_func, params in tools_and_params:
            result = await tool_func.fn(**params)
            assert "OPENAI_API_KEY environment variable not set" in result


@pytest.mark.integration
class TestCodexToolsIntegration:
    """Integration tests for Codex tools (require actual API key)."""
    
    @pytest.mark.skipif(
        not os.getenv("RUN_INTEGRATION_TESTS"),
        reason="Integration tests require RUN_INTEGRATION_TESTS environment variable"
    )
    @pytest.mark.asyncio
    async def test_codex_generate_real_api(self):
        """Test actual API integration for code generation."""
        # This test requires a real API key and --run-integration flag
        result = await codex_generate.fn(
            prompt="Create a simple function that adds two numbers",
            language="python",
            temperature=0.1
        )
        
        assert "def " in result
        assert "return" in result
        assert "Error" not in result
    
    @pytest.mark.skipif(
        not os.getenv("RUN_INTEGRATION_TESTS"),
        reason="Integration tests require RUN_INTEGRATION_TESTS environment variable"
    )
    @pytest.mark.asyncio
    async def test_codex_tools_workflow(self):
        """Test a complete workflow: generate -> review -> refactor -> explain."""
        # Generate code
        generated = await codex_generate.fn(
            prompt="Create a function to validate email addresses",
            language="python",
            temperature=0.1
        )
        assert "def " in generated
        
        # Extract just the code (simple extraction for test)
        code_lines = [line for line in generated.split('\n') if line.strip() and not line.strip().startswith('#')]
        code_sample = '\n'.join(code_lines)
        
        # Review the generated code
        review = await codex_review.fn(code=code_sample, focus="security")
        assert "Assessment" in review or "review" in review.lower()
        
        # Refactor for improvements  
        refactored = await codex_refactor.fn(
            code=code_sample,
            requirements="Add comprehensive error handling and type hints"
        )
        assert "refactor" in refactored.lower() or "def " in refactored
        
        # Explain the final code
        explanation = await codex_explain.fn(
            code=code_sample,
            level="detailed",
            audience="developer"
        )
        assert len(explanation) > 100  # Substantial explanation
        assert "Error" not in explanation


# Pytest configuration for integration tests
def pytest_addoption(parser):
    """Add command line option for integration tests."""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests that require API access"
    )


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "integration: mark test as integration test requiring API access")


def pytest_collection_modifyitems(config, items):
    """Skip integration tests unless explicitly requested."""
    if config.getoption("--run-integration"):
        return
    
    skip_integration = pytest.mark.skip(reason="need --run-integration option to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)