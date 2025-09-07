# Shared Test Utilities

Reusable testing components for MCP server testing framework.

## Base Test Classes (`base_test_classes.py`)

### `AsyncTestBase`
Foundation class for all async MCP server tests.

```python
class MyTest(AsyncTestBase):
    async def test_something(self):
        # Automatically handles async setup/teardown
        result = await self.async_operation()
```

**Features:**
- Async test lifecycle management
- Event loop configuration
- Common assertion helpers

### Mixins

#### `ProtocolComplianceMixin`
Validates MCP protocol specification adherence.

```python
class TestProtocol(AsyncTestBase, ProtocolComplianceMixin):
    async def test_request_format(self):
        response = await self.server.method()
        self.assert_mcp_compliant(response)
```

**Validation Features:**
- Request/response format validation
- Required field verification
- Type checking for MCP data structures

#### `ErrorSimulationMixin` 
Simulates various failure scenarios.

```python
class TestErrors(AsyncTestBase, ErrorSimulationMixin):
    async def test_network_failure(self):
        with self.simulate_network_timeout():
            response = await self.server.method()
            self.assert_error_handled(response)
```

**Simulation Types:**
- Network timeouts and connection failures
- API rate limiting and quota exhaustion
- Malformed response data
- Authentication failures

#### `PerformanceTestMixin`
Automatic performance monitoring and baseline validation.

```python
class TestPerformance(AsyncTestBase, PerformanceTestMixin):
    async def test_fast_operation(self):
        # Performance automatically tracked
        result = await self.server.health_check()
        # Baseline validation happens automatically
```

**Features:**
- Automatic timing measurement using `time.perf_counter()`
- Baseline comparison with configurable thresholds
- Performance regression detection
- Metrics aggregation and reporting

## Mock Factories (`mock_factories.py`)

Standardized mock response generators that prevent accidental API calls.

### `PerplexityMockFactory`
Generates realistic Perplexity API responses.

```python
# Simple mock
mock_client = PerplexityMockFactory.create_client_mock()

# Custom responses
responses = [
    PerplexityMockFactory.create_search_response("AI research"),
    PerplexityMockFactory.create_research_response("Deep analysis")
]
mock_client = PerplexityMockFactory.create_client_mock(responses)
```

**Response Types:**
- `create_search_response()` - Search query results
- `create_research_response()` - Deep research analysis
- `create_error_response()` - API error scenarios

### `OpenAIMockFactory`
Generates OpenAI structured output responses.

```python
# Structured data extraction
mock_response = OpenAIMockFactory.create_extraction_response({
    "entities": ["OpenAI", "Python"],
    "confidence": 0.95
})

# Code analysis
mock_response = OpenAIMockFactory.create_code_analysis_response({
    "complexity_score": 3,
    "issues": ["Missing docstrings"],
    "functions_count": 5
})
```

**Response Types:**
- `create_extraction_response()` - Data extraction results
- `create_code_analysis_response()` - Code analysis outputs
- `create_task_response()` - Configuration task responses
- `create_sentiment_response()` - Sentiment analysis results

### `ErrorScenarioFactory`
Generates various error conditions for testing.

```python
# Network errors
error_response = ErrorScenarioFactory.network_timeout()

# API errors  
error_response = ErrorScenarioFactory.api_quota_exceeded()

# Malformed responses
error_response = ErrorScenarioFactory.malformed_json()
```

**Error Types:**
- Network failures (timeouts, connection refused)
- API errors (authentication, rate limits, quotas)
- Data format errors (malformed JSON, missing fields)
- Server errors (5xx responses, service unavailable)

### `GenericMockFactory`
Generic mock utilities for common test scenarios.

```python
# HTTP response mocking
mock_response = GenericMockFactory.http_response(200, {"status": "ok"})

# Async mock creation
async_mock = GenericMockFactory.async_mock(return_value="result")
```

## Performance Utilities (`performance_utils.py`)

### `PerformanceTracker`
Records and analyzes performance metrics.

```python
tracker = PerformanceTracker()
tracker.record('health_check', duration_ms=45.2)

# Get statistics
stats = tracker.get_statistics('health_check')
print(f"Average: {stats.mean_ms}ms, P95: {stats.percentile_95_ms}ms")

# Validate against baselines
violations = tracker.validate_baselines()
```

**Features:**
- Configurable baseline loading from YAML
- Environment-specific threshold adjustments
- Statistical analysis (mean, median, percentiles)
- Baseline violation detection

### `PerformanceTester`
Higher-level performance testing utilities.

```python
@PerformanceTester.measure('complex_query')
async def test_operation():
    return await server.complex_operation()

# Results automatically recorded and validated
```

**Decorators:**
- `@measure(operation_name)` - Automatic timing and recording
- `@baseline_required(operation_name)` - Enforce baseline compliance
- `@performance_regression_check` - Compare against historical data

## Import Structure

Individual MCP servers import shared utilities via repository root path:

```python
# In perplexity-mcp/tests/conftest.py
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Now imports work from individual server tests
from tests.shared.base_test_classes import AsyncTestBase
from tests.shared.mock_factories import PerplexityMockFactory
```

This structure allows:
- **Code reuse** across different MCP servers
- **Consistent testing patterns** and utilities
- **Centralized mock management** and updates
- **Shared performance baselines** and validation logic

## Best Practices

1. **Always use mock factories** instead of hardcoded responses
2. **Extend base classes** rather than implementing async handling manually  
3. **Use mixins** for cross-cutting testing concerns
4. **Leverage performance tracking** for regression detection
5. **Keep mocks realistic** but obviously fake (especially API keys)
6. **Document custom mock responses** for complex test scenarios