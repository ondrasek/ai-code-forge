# Launcher Testing Documentation

## Overview

The AI Code Forge launcher ecosystem includes comprehensive testing infrastructure to ensure security, functionality, and consistency across the launcher scripts. This document provides guidance for running tests, interpreting results, and maintaining test quality.

## Test Infrastructure

### Test Suite Architecture
```
scripts/tests/
├── test-launcher-security.sh      # Security validation tests
├── test-launcher-units.sh          # Unit tests for core functions
├── test-launcher-integration.sh    # CLI interface and workflow tests
└── run-all-tests.sh               # Master test runner
```

### Components Under Test
- **`scripts/lib/launcher-utils.sh`** - Shared utility library
- **`scripts/launch-codex.sh`** - OpenAI Codex CLI wrapper
- **`scripts/launch-claude.sh`** - Claude Code wrapper

## Running Tests

### Quick Start
```bash
# Run all test suites with summary output
./scripts/tests/run-all-tests.sh

# Run with detailed output
./scripts/tests/run-all-tests.sh --verbose

# Stop on first failure (for debugging)
./scripts/tests/run-all-tests.sh --stop-on-fail
```

### Individual Test Suites
```bash
# Security tests (critical for production deployment)
./scripts/tests/test-launcher-security.sh

# Unit tests (core functionality validation)
./scripts/tests/test-launcher-units.sh

# Integration tests (CLI interface consistency)
./scripts/tests/test-launcher-integration.sh
```

## Test Categories

### 1. Security Tests (`test-launcher-security.sh`)
**Priority: CRITICAL** - Must pass before production deployment

#### Test Coverage:
- **Command Injection Prevention** - Validates blocking of malicious environment variables
- **File Validation Security** - Tests permission checking and size limits
- **Path Traversal Prevention** - Ensures safe handling of file paths
- **Environment Variable Validation** - Tests proper variable name formatting
- **Session Logging Security** - Validates secure log directory creation
- **Tool Validation Security** - Tests rejection of malicious tool names

#### Example Output:
```
✓ PASS: Command Injection Prevention
✗ FAIL: Environment File Validation Security
  Details: SECURITY FAILURE: No warning for world-readable file
```

### 2. Unit Tests (`test-launcher-units.sh`)
**Priority: HIGH** - Validates core functionality

#### Test Coverage:
- **Environment Detection** - Container vs local environment identification
- **Path Initialization** - Correct SCRIPT_DIR and PROJECT_ROOT setup
- **Tool Requirements Validation** - Dependency checking
- **Configuration Loading** - .env file processing with precedence
- **Session Management** - Log directory and file creation
- **Environment Variable Masking** - Sensitive value protection in debug output

#### Example Output:
```
✓ PASS: Environment Detection Scenarios
✓ PASS: Tool Requirements Validation
✗ FAIL: Configuration Loading
  Details: load_configuration failed: VAR2=value2 (expected: overridden_value)
```

### 3. Integration Tests (`test-launcher-integration.sh`)
**Priority: MEDIUM** - Ensures CLI consistency

#### Test Coverage:
- **CLI Help Interface Consistency** - Consistent help output between launchers
- **Dry Run Mode Functionality** - Command construction without execution
- **Error Handling** - Invalid option rejection
- **Logging Directory Creation** - End-to-end logging setup
- **Environment Detection Consistency** - Same environment detection across launchers
- **Configuration File Handling** - .env file loading integration
- **Codex-Specific Features** - Authentication modes, approval modes, profiles

#### Example Output:
```
✓ PASS: CLI Help Interface Consistency
✓ PASS: Dry Run Mode Functionality
✗ FAIL: Configuration File Handling
  Details: Configuration file loading may not be working consistently
```

## Test Results Interpretation

### Success Indicators
- **All security tests pass** - Critical for production deployment
- **Unit test coverage >90%** - Core functionality validated
- **Integration tests pass** - CLI interfaces consistent

### Failure Categories

#### Critical Failures (Block Deployment)
- **Security test failures** - Injection vulnerabilities, permission issues
- **Core function failures** - Environment detection, configuration loading

#### Medium Priority Failures
- **CLI inconsistencies** - Different behavior between launchers
- **Edge case handling** - Unexpected input scenarios

#### Low Priority Failures
- **Performance issues** - Slow operations (not correctness)
- **Cosmetic issues** - Output formatting inconsistencies

### Example Summary Output
```
╔══════════════════════════════════════════════════════════════╗
║                    TEST SUMMARY                             ║
╠══════════════════════════════════════════════════════════════╣
║ Total Tests:  25                                           ║
║ Passed:       18                                           ║
║ Failed:        7                                           ║
║ Duration:     15s                                          ║
╚══════════════════════════════════════════════════════════════╝

⚠️  SOME TESTS FAILED
Critical issues detected in launcher ecosystem

Recommended actions:
• Review failed test details above
• Fix security and functionality issues
• Re-run tests before deployment
```

## CI/CD Integration

### GitHub Actions Integration
```yaml
# .github/workflows/launcher-tests.yml
name: Launcher Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Launcher Tests
        run: ./scripts/tests/run-all-tests.sh
      - name: Upload Test Results
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: /tmp/launcher-*-test-*/
```

### Exit Codes
- **0** - All tests passed
- **1** - Some tests failed (check output for details)

### Pre-commit Hook Integration
```bash
#!/bin/bash
# .git/hooks/pre-commit
set -e

# Run launcher tests before commit
if [[ -f "./scripts/tests/run-all-tests.sh" ]]; then
    echo "Running launcher tests..."
    ./scripts/tests/run-all-tests.sh
fi
```

## Debugging Test Failures

### Security Test Failures
1. **Check file permissions** - Ensure test environment has proper permissions
2. **Verify injection patterns** - Update security patterns in launcher-utils.sh
3. **Review environment variables** - Validate test environment setup

### Unit Test Failures
1. **Check function isolation** - Ensure tests don't interfere with each other
2. **Verify mock data** - Confirm test fixtures are properly created
3. **Review environment cleanup** - Ensure proper test teardown

### Integration Test Failures
1. **Check script dependencies** - Ensure all required tools are available
2. **Verify file paths** - Confirm scripts exist and are executable
3. **Review output parsing** - Update expected output patterns if needed

## Debugging Commands

### Manual Testing
```bash
# Source utilities directly for debugging
source scripts/lib/launcher-utils.sh

# Test individual functions
detect_environment
echo "Environment: $DETECTED_ENV_TYPE, Skip: $DETECTED_SKIP_PERMISSIONS"

# Test configuration loading
load_configuration "$(pwd)" true

# Test with specific environment variables
CODESPACES=true detect_environment
```

### Verbose Test Output
```bash
# Run specific test with debug output
bash -x scripts/tests/test-launcher-security.sh

# Check individual test functions
grep -A 20 "test_command_injection_prevention" scripts/tests/test-launcher-security.sh
```

## Maintaining Test Quality

### Adding New Tests
1. **Follow established patterns** - Use existing test structure
2. **Include cleanup** - Ensure proper teardown in all tests
3. **Test edge cases** - Include boundary conditions and error scenarios
4. **Document purpose** - Clear comments explaining test objectives

### Test Data Management
```bash
# Test fixtures location
TEST_TEMP_DIR="/tmp/launcher-*-test-$$"

# Example test fixture creation
cat > "$TEST_TEMP_DIR/test.env" << 'EOF'
SAFE_VAR=value
DANGEROUS_VAR=$(rm -rf /)
EOF
```

### Performance Considerations
- **Test execution time** - Keep individual tests under 30 seconds
- **Resource usage** - Clean up temporary files and processes
- **Parallel execution** - Ensure tests can run concurrently

## Test Coverage Goals

### Current Coverage
- **Security Tests**: 8 test cases covering critical attack vectors
- **Unit Tests**: 8 test cases covering core functions  
- **Integration Tests**: 9 test cases covering CLI workflows

### Target Coverage
- **Line Coverage**: 85% for security-critical functions
- **Branch Coverage**: 90% for error handling paths
- **Function Coverage**: 100% for public API functions

## Common Issues and Solutions

### Permission Denied Errors
```bash
# Make all test scripts executable
chmod +x scripts/tests/*.sh

# Fix temporary directory permissions
chmod 755 /tmp/launcher-*-test-*
```

### Environment Variable Conflicts
```bash
# Clear test variables before running
unset TEST_VAR1 TEST_VAR2 API_KEY TOKEN

# Use isolated test environment
env -i bash scripts/tests/run-all-tests.sh
```

### Docker/Container Issues
```bash
# Run tests in container-aware mode
DEVCONTAINER=true ./scripts/tests/run-all-tests.sh

# Mount test directories properly
docker run -v $(pwd):/workspace -w /workspace ubuntu:latest ./scripts/tests/run-all-tests.sh
```

## Contributing to Tests

### Test Development Guidelines
1. **Security First** - Always test security-critical functionality
2. **Reproducible Results** - Tests should produce consistent results
3. **Clear Failure Messages** - Provide actionable error information
4. **Minimal Dependencies** - Use standard shell tools when possible

### Code Review Checklist
- [ ] Tests cover new functionality
- [ ] Security implications considered
- [ ] Edge cases included
- [ ] Cleanup functions implemented
- [ ] Documentation updated

## Future Enhancements

### Planned Improvements
- **Performance benchmarking** - Execution time validation
- **Load testing** - Concurrent execution testing
- **Cross-platform testing** - macOS, Windows compatibility
- **Container simulation** - Docker-based environment testing

### Monitoring and Metrics
- **Test execution trends** - Track performance over time
- **Failure pattern analysis** - Identify recurring issues
- **Coverage tracking** - Monitor test coverage improvements