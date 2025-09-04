# Git Integration Testing

This directory contains comprehensive automated tests for the ACF CLI git integration functionality.

## Test Structure

### Unit Tests (`test_git_integration_unit.py`)
- **GitCommandWrapper methods**: Test individual wrapper methods in isolation
- **Commit message generation**: Verify correct commit message formats for different scenarios
- **Error handling**: Test error scenarios and edge cases
- **Mocking**: Uses mocks to test logic without actual git operations

### Integration Tests (`test_git_integration_e2e.py`)
- **End-to-end workflows**: Test complete command + git integration workflows
- **Real git operations**: Uses actual git repositories and commits
- **Multiple commands**: Tests both `init` and `update` commands with git integration
- **Repository validation**: Verifies git integration doesn't break core functionality

## Running Tests

### Quick Smoke Test
```bash
# Run a fast subset of tests to verify basic functionality
python tests/run_git_tests.py --smoke
```

### Full Test Suite
```bash
# Run all git integration tests
python tests/run_git_tests.py
```

### Individual Test Files
```bash
# Run only unit tests
PYTHONPATH=src python -m pytest tests/test_git_integration_unit.py -v

# Run only integration tests
PYTHONPATH=src python -m pytest tests/test_git_integration_e2e.py -v
```

### Specific Test Cases
```bash
# Test commit message generation
PYTHONPATH=src python -m pytest tests/test_git_integration_unit.py::TestGitCommandWrapper::test_generate_commit_message_update -v

# Test init command with git
PYTHONPATH=src python -m pytest tests/test_git_integration_e2e.py::TestGitIntegrationE2E::test_init_with_git_creates_commit -v
```

## Test Scenarios Covered

### Unit Test Coverage
- ✅ GitCommandWrapper initialization
- ✅ Git repository detection logic
- ✅ Commit message generation (all formats)
- ✅ ACF file patterns for git operations
- ✅ Version detection from state files
- ✅ Error handling (git not configured, add failure, commit failure)
- ✅ Factory function (`create_git_wrapper`)

### Integration Test Coverage
- ✅ `init` command with `--git` flag creates commit
- ✅ `init` command without `--git` flag skips git
- ✅ `init` with `--git` and `--dry-run` skips commit
- ✅ `update` command with `--git` flag creates commit
- ✅ Git integration error handling (non-git directories)
- ✅ Commit message format validation
- ✅ Multiple commands create separate commits
- ✅ Git integration preserves core functionality
- ✅ Git integration works with existing repository content

## Fixtures Available

### Standard Fixtures (from `conftest.py`)
- `temp_repo`: Temporary directory for testing
- `real_git_repo`: Real git repository with proper initialization
- `git_repo_with_commits`: Git repository with existing commits

### Usage Examples

```python
def test_my_git_feature(real_git_repo):
    """Test using a real git repository."""
    # Repository is already initialized with git
    # Has git user configured for testing
    
def test_with_existing_content(git_repo_with_commits):
    """Test with pre-existing repository content."""
    # Repository has README.md committed
    # Perfect for testing git integration with existing files
```

## Expected Commit Message Formats

The git integration creates commits with these patterns:

- **Initial deployment**: `chore: acforge init configuration (v{version})`
- **Version update**: `chore: acforge update configuration ({old_version} → {new_version})`
- **Same version**: `chore: acforge {command} configuration (v{version})`
- **No version**: `chore: acforge {command} configuration update`

## Continuous Integration

These tests are designed to run in CI environments:

- **No external dependencies**: Only requires git (available in most CI)
- **Isolated repositories**: Each test uses temporary directories
- **Fast execution**: Unit tests run in <1s, integration tests in <5s
- **Clear failure reporting**: Descriptive assertions and error messages

## Troubleshooting

### Test Failures

If tests fail, check:

1. **Git availability**: Ensure `git` command is in PATH
2. **Python path**: Verify `PYTHONPATH` includes CLI source directory
3. **Permissions**: Ensure test runner has write permissions for temp directories

### Common Issues

- **"git not found"**: Install git or ensure it's in PATH
- **"No module named ai_code_forge_cli"**: Set `PYTHONPATH=src` before running pytest
- **Permission errors**: Run tests from project directory with appropriate permissions

## Adding New Tests

### For new git integration features:

1. Add unit tests in `test_git_integration_unit.py` for isolated logic testing
2. Add integration tests in `test_git_integration_e2e.py` for end-to-end workflows
3. Update this README with new scenarios covered
4. Run smoke test to verify new tests work correctly

### Test naming conventions:

- Unit tests: `test_{component}_{behavior}`
- Integration tests: `test_{command}_with_git_{expected_outcome}`
- Error tests: `test_{component}_{error_scenario}`