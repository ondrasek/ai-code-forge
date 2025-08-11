# MCP Server Testing Framework

Comprehensive testing infrastructure for Model Context Protocol (MCP) servers with performance monitoring, error simulation, and integration testing.

## Architecture Overview

The testing framework is organized into several specialized layers:

```
tests/
├── shared/           # Reusable testing utilities and base classes
├── config/           # Configuration files for baselines and settings
├── benchmark/        # Performance baseline validation tests
├── integration/      # Cross-server and workflow integration tests
├── load/            # Concurrent connection and resource exhaustion tests
├── security/        # Security and injection attack prevention tests
├── unit/            # Unit-level validation functions
└── validation/      # Acceptance criteria validation tests
```

## Key Components

### Shared Testing Infrastructure

**Location:** `tests/shared/`

- **`base_test_classes.py`** - Base classes with mixins for different test types
- **`mock_factories.py`** - Standardized mock response generators for APIs
- **`performance_utils.py`** - Performance tracking and baseline validation utilities

### Performance Baseline System

**Configuration:** `tests/config/performance_baselines.yaml`

Environment-aware performance thresholds that can be adjusted per deployment context:

```yaml
baselines:
  health_check:
    max_duration_ms: 100
    percentile_95_ms: 50
    
environments:
  ci:
    multiplier: 1.5    # CI environments get 50% more time
  local:
    multiplier: 0.8    # Local development expects faster performance
```

**Environment Variable:** `PERFORMANCE_TEST_ENV` (defaults to "local")

### Import Structure

Individual MCP server tests (`perplexity-mcp/tests/`, `openai-structured-mcp/tests/`) import shared utilities via:

```python
from tests.shared.base_test_classes import AsyncTestBase, ProtocolComplianceMixin
from tests.shared.mock_factories import PerplexityMockFactory
```

This is enabled by adding the repository root to `sys.path` in each server's `conftest.py`.

## Test Categories

### 1. Protocol Compliance Tests
- **Location:** Individual server `tests/test_protocol_compliance.py`
- **Purpose:** Validate MCP specification adherence
- **Coverage:** Request/response formats, error handling, capability negotiation

### 2. Error Handling Tests
- **Location:** Individual server `tests/test_error_handling.py` 
- **Purpose:** Simulate failure scenarios and validate recovery
- **Coverage:** Network timeouts, API failures, malformed responses

### 3. Performance Baseline Tests
- **Location:** `tests/benchmark/test_performance_baselines.py`
- **Purpose:** Validate operations meet performance requirements
- **Coverage:** Response times, throughput, resource utilization

### 4. Integration Tests
- **Location:** `tests/integration/`
- **Purpose:** Cross-server coordination and workflow validation
- **Coverage:** Claude Code workflows, multi-server operations

### 5. Load Tests  
- **Location:** `tests/load/`
- **Purpose:** Validate behavior under concurrent load
- **Coverage:** Connection pooling, resource exhaustion, scaling limits

## Running Tests

### Prerequisites

Install test dependencies:

```bash
# From repository root
pip install -e ".[dev]"

# Or for individual servers
cd mcp-servers/perplexity-mcp && pip install -e ".[dev]" && cd ../..
cd mcp-servers/openai-structured-mcp && pip install -e ".[dev]" && cd ../..
```

### Environment Setup

Set test environment (affects performance baselines):

```bash
export PERFORMANCE_TEST_ENV=local  # or ci, production
```

### Execution Commands

#### Recommended: Use Test Runner Scripts

**From repository root:**
```bash
# Simple shell script wrapper
mcp-servers/tests/run_tests.sh                    # Run all tests
mcp-servers/tests/run_tests.sh --verbose          # Detailed output
mcp-servers/tests/run_tests.sh --env ci           # CI environment baselines
mcp-servers/tests/run_tests.sh --quick            # Fast unit tests only
mcp-servers/tests/run_tests.sh --coverage         # Generate coverage report
mcp-servers/tests/run_tests.sh --include-slow     # Include load tests

# Direct Python script (more options)
cd mcp-servers && python tests/run_tests.py --help
```

**Features of the test runner:**
- ✅ **Dependency checking** - Verifies required packages are installed
- ✅ **Environment setup** - Automatically sets PERFORMANCE_TEST_ENV
- ✅ **Comprehensive coverage** - Runs all test categories in logical order
- ✅ **Error reporting** - Clear success/failure indicators with timing
- ✅ **Flexible options** - Quick mode, coverage, verbose output
- ✅ **Load test safety** - Resource-intensive tests are optional

#### Manual pytest Commands

**From repository root:**
```bash
# Run all tests
pytest mcp-servers/tests/

# Run specific test categories
pytest mcp-servers/tests/benchmark/           # Performance tests
pytest mcp-servers/tests/integration/        # Integration tests
pytest mcp-servers/perplexity-mcp/tests/    # Perplexity server tests

# Run with performance reporting
pytest mcp-servers/tests/benchmark/ -v --tb=short

# Run load tests (warning: resource intensive)  
pytest mcp-servers/tests/load/ -v -s
```

### Test Configuration

Each MCP server includes `conftest.py` with:
- Mock environment variables (with obviously fake API keys)
- Async event loop configuration
- Server-specific fixtures and mock responses

## Security Features

- **Fake API Keys:** All tests use obviously fake keys like `sk-test-fake-openai-key-do-not-use`
- **Mock Factories:** Standardized mock responses prevent accidental API calls
- **Environment Isolation:** Tests never use real API endpoints

## Performance Monitoring

The framework includes built-in performance tracking:

```python
# Automatic tracking via mixins
class MyTest(AsyncTestBase, PerformanceTestMixin):
    async def test_operation(self):
        # Performance automatically recorded
        result = await self.server.operation()
```

Performance metrics are validated against configurable baselines with environment-specific adjustments.

## Troubleshooting

### Import Errors
If you see `ModuleNotFoundError: No module named 'tests.shared'`:
- Ensure you're running tests from the repository root
- Check that `conftest.py` includes the sys.path modification

### Performance Test Failures
If performance tests fail unexpectedly:
- Check `PERFORMANCE_TEST_ENV` environment variable
- Adjust multipliers in `tests/config/performance_baselines.yaml`
- Consider system load and available resources

### Dependency Issues
If you see `ModuleNotFoundError: No module named 'psutil'`:
- Install development dependencies: `pip install -e ".[dev]"`
- Ensure psutil is in the dev-dependencies list