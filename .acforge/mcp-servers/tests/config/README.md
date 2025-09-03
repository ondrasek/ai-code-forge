# Test Configuration

Configuration files for the MCP server testing framework.

## Performance Baselines (`performance_baselines.yaml`)

Defines performance thresholds and environment-specific adjustments for MCP server operations.

### Structure

```yaml
baselines:
  operation_name:
    max_duration_ms: 1000      # Maximum acceptable duration
    percentile_95_ms: 800      # 95th percentile target
    description: "Human readable description"

environments:
  env_name:
    multiplier: 1.5            # Adjustment factor for this environment

settings:
  default_environment: "local"
  enable_warnings: true
  fail_on_baseline_violations: true
```

### Supported Operations

- **`health_check`** - Basic server health verification
- **`simple_query`** - Single API request operations  
- **`complex_query`** - Multi-step or complex processing
- **`structured_extraction`** - OpenAI structured output operations
- **`code_analysis`** - Code processing and analysis tasks
- **`batch_operation`** - Operations on multiple items

### Environment Multipliers

- **`local`** (0.8x) - Optimized development environment
- **`ci`** (1.5x) - CI environments with potential resource constraints
- **`production`** (1.0x) - Production baseline requirements

### Usage

Set environment via environment variable:
```bash
export PERFORMANCE_TEST_ENV=ci
pytest tests/benchmark/
```

### Customization

To add new operation baselines:

1. Add entry to `baselines` section
2. Define `max_duration_ms` and `percentile_95_ms` thresholds
3. Include descriptive `description`
4. Test with: `pytest tests/benchmark/ -k your_operation`

### Fallback Behavior

If configuration file is missing or invalid, the system falls back to hardcoded defaults with a warning message. This ensures tests remain functional during development.