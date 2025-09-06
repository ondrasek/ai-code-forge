"""Base test classes for MCP server testing."""

import pytest
import asyncio
import time
import json
from typing import Dict, Any, Optional
from unittest.mock import AsyncMock, MagicMock


class MCPServerTestBase:
    """Base test class for MCP server implementations."""
    
    def setup_method(self):
        """Setup method called before each test."""
        self.start_time = time.time()
        self.performance_threshold_ms = 1000  # 1 second default
    
    def teardown_method(self):
        """Teardown method called after each test."""
        duration_ms = (time.time() - self.start_time) * 1000
        if hasattr(self, '_test_performance_tracking'):
            print(f"Test duration: {duration_ms:.2f}ms")
    
    def assert_performance_threshold(self, threshold_ms: Optional[int] = None):
        """Assert that test execution is within performance threshold."""
        duration_ms = (time.time() - self.start_time) * 1000
        threshold = threshold_ms or self.performance_threshold_ms
        assert duration_ms <= threshold, f"Test exceeded performance threshold: {duration_ms:.2f}ms > {threshold}ms"
    
    def assert_valid_json_response(self, response: str) -> Dict[Any, Any]:
        """Assert response is valid JSON and return parsed data."""
        try:
            parsed = json.loads(response)
            assert isinstance(parsed, dict), "Response must be a JSON object"
            return parsed
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON response: {e}")
    
    def assert_mcp_response_structure(self, response: Dict[Any, Any], required_fields: list = None):
        """Assert MCP response has expected structure."""
        if required_fields is None:
            required_fields = ['success', 'data']
        
        for field in required_fields:
            assert field in response, f"Missing required field: {field}"
    
    def create_mock_client(self, client_type: str = "generic") -> AsyncMock:
        """Create a mock client for testing."""
        mock_client = AsyncMock()
        
        if client_type == "perplexity":
            mock_client.AVAILABLE_MODELS = ["sonar", "sonar-pro", "sonar-reasoning", "sonar-deep-research"]
            mock_client.health_check.return_value = True
            mock_client.query.return_value = {
                "choices": [{"message": {"content": "Test response"}}]
            }
        elif client_type == "openai":
            mock_client.get_available_schemas.return_value = {
                "data_extraction": "Extract structured data",
                "code_analysis": "Analyze code",
                "sentiment_analysis": "Analyze sentiment"
            }
            mock_client.health_check.return_value = True
            mock_client.structured_completion.return_value = {
                "success": True,
                "data": {"test": "data"}
            }
        
        return mock_client


class AsyncTestBase(MCPServerTestBase):
    """Base class for async MCP server tests."""
    
    @pytest.fixture(autouse=True)
    def setup_async_test(self):
        """Setup async test environment."""
        self.loop = asyncio.get_event_loop()
    
    async def assert_async_performance_threshold(self, coro, threshold_ms: int = 1000):
        """Assert async operation completes within threshold."""
        start_time = time.time()
        result = await coro
        duration_ms = (time.time() - start_time) * 1000
        assert duration_ms <= threshold_ms, f"Async operation exceeded threshold: {duration_ms:.2f}ms > {threshold_ms}ms"
        return result


class PerformanceTestMixin:
    """Mixin for performance testing capabilities."""
    
    def _init_performance_baselines(self):
        """Initialize performance baselines if not already set."""
        if not hasattr(self, 'performance_baselines'):
            self.performance_baselines = {
                'health_check': 100,  # ms
                'simple_query': 500,  # ms
                'complex_query': 2000,  # ms
                'batch_operation': 5000  # ms
            }
    
    def record_performance(self, operation: str, duration_ms: float):
        """Record performance metrics for analysis."""
        if not hasattr(self, '_performance_data'):
            self._performance_data = {}
        
        if operation not in self._performance_data:
            self._performance_data[operation] = []
        
        self._performance_data[operation].append(duration_ms)
    
    def assert_performance_baseline(self, operation: str, duration_ms: float):
        """Assert operation meets performance baseline."""
        self._init_performance_baselines()
        baseline = self.performance_baselines.get(operation, 1000)
        assert duration_ms <= baseline, f"{operation} exceeded baseline: {duration_ms:.2f}ms > {baseline}ms"
    
    def get_performance_summary(self) -> Dict[str, Dict[str, float]]:
        """Get performance summary statistics."""
        if not hasattr(self, '_performance_data'):
            return {}
        
        summary = {}
        for operation, measurements in self._performance_data.items():
            summary[operation] = {
                'min': min(measurements),
                'max': max(measurements),
                'avg': sum(measurements) / len(measurements),
                'count': len(measurements)
            }
        
        return summary


class ErrorSimulationMixin:
    """Mixin for error simulation and testing."""
    
    def create_network_error_mock(self, error_type: str = "connection") -> Exception:
        """Create appropriate network error for testing."""
        if error_type == "connection":
            return ConnectionError("Network connection failed")
        elif error_type == "timeout":
            return TimeoutError("Request timed out")
        elif error_type == "http":
            return Exception("HTTP 500 Internal Server Error")
        else:
            return Exception(f"Unknown {error_type} error")
    
    def create_api_error_response(self, error_type: str = "auth") -> Dict[str, Any]:
        """Create API error response for testing."""
        if error_type == "auth":
            return {"error": "Invalid API key", "error_type": "authentication"}
        elif error_type == "rate_limit":
            return {"error": "Rate limit exceeded", "error_type": "rate_limit"}
        elif error_type == "quota":
            return {"error": "Quota exceeded", "error_type": "quota_exceeded"}
        else:
            return {"error": f"Generic {error_type} error", "error_type": "generic"}


class ProtocolComplianceMixin:
    """Mixin for MCP protocol compliance testing."""
    
    def assert_tool_registration(self, tools: list, required_tools: list):
        """Assert all required tools are properly registered."""
        tool_names = [tool.get('name', '') for tool in tools]
        for required_tool in required_tools:
            assert required_tool in tool_names, f"Missing required tool: {required_tool}"
    
    def assert_tool_schema_compliance(self, tool_schema: Dict[str, Any]):
        """Assert tool schema follows MCP protocol."""
        required_fields = ['name', 'description', 'inputSchema']
        for field in required_fields:
            assert field in tool_schema, f"Tool schema missing required field: {field}"
        
        # Validate input schema structure
        input_schema = tool_schema['inputSchema']
        assert 'type' in input_schema, "Input schema must specify type"
        assert input_schema['type'] == 'object', "Input schema type must be 'object'"
        assert 'properties' in input_schema, "Input schema must have properties"
    
    def assert_response_format_compliance(self, response: Dict[str, Any], expected_format: str = "tool_result"):
        """Assert response follows MCP format specifications."""
        if expected_format == "tool_result":
            assert 'content' in response or 'error' in response, "Tool result must have content or error"
            if 'content' in response:
                assert isinstance(response['content'], (str, list)), "Content must be string or list"
        elif expected_format == "error":
            assert 'error' in response, "Error response must have error field"
            assert 'message' in response['error'] or isinstance(response['error'], str), "Error must have message"
