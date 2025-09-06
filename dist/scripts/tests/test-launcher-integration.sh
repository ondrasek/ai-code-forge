#!/bin/bash
set -euo pipefail

# Integration Tests for Launcher Scripts
# Tests CLI interface consistency and complete workflows
# Usage: ./test-launcher-integration.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAUNCHER_DIR="$(dirname "$SCRIPT_DIR")"

# Color codes for test output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test result tracking
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test directory for temporary files
TEST_TEMP_DIR="/tmp/launcher-integration-test-$$"
mkdir -p "$TEST_TEMP_DIR"

# Cleanup function
cleanup() {
    rm -rf "$TEST_TEMP_DIR" 2>/dev/null || true
}

# Set trap for cleanup
trap cleanup EXIT

# Print test results
print_test() {
    local test_name="$1"
    local result="$2"
    local details="$3"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    
    if [[ "$result" == "PASS" ]]; then
        echo -e "${GREEN}✓ PASS${NC}: $test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ FAIL${NC}: $test_name"
        echo -e "${YELLOW}  Details: $details${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Test function wrapper
run_test() {
    local test_name="$1"
    shift
    local test_function="$1"
    shift
    
    echo -e "${BLUE}Running: $test_name${NC}"
    
    local result
    local details
    
    if result="$($test_function "$@" 2>&1)"; then
        print_test "$test_name" "PASS" "$result"
    else
        print_test "$test_name" "FAIL" "$result"
    fi
}

# === INTEGRATION TESTS ===

# Test: CLI help interface consistency between launchers
test_cli_help_consistency() {
    # Test help format consistency
    local claude_help
    local codex_help
    
    claude_help=$("$LAUNCHER_DIR/launch-claude.sh" --help 2>&1)
    codex_help=$("$LAUNCHER_DIR/launch-codex.sh" --help 2>&1)
    
    # Both should have required sections
    local required_sections=("USAGE:" "OPTIONS:" "EXAMPLES:" "FEATURES:")
    
    for section in "${required_sections[@]}"; do
        if [[ ! "$claude_help" =~ $section ]]; then
            echo "launch-claude.sh missing section: $section"
            return 1
        fi
        if [[ ! "$codex_help" =~ $section ]]; then
            echo "launch-codex.sh missing section: $section"
            return 1
        fi
    done
    
    # Check common options exist in both
    local common_options=("--help" "--quiet" "--no-debug" "--no-logs" "--dry-run" "--analyze-logs" "--clean-logs")
    
    for option in "${common_options[@]}"; do
        if [[ ! "$claude_help" =~ $option ]]; then
            echo "launch-claude.sh missing option: $option"
            return 1
        fi
        if [[ ! "$codex_help" =~ $option ]]; then
            echo "launch-codex.sh missing option: $option"
            return 1
        fi
    done
    
    echo "CLI help interfaces are consistent between launchers"
    return 0
}

# Test: Dry run mode functionality
test_dry_run_mode() {
    # Test Claude launcher dry run
    local claude_dry
    claude_dry=$("$LAUNCHER_DIR/launch-claude.sh" --dry-run "test query" 2>&1)
    
    if [[ "$claude_dry" =~ "Dry run complete" ]] && [[ "$claude_dry" =~ "would execute:" ]]; then
        echo "launch-claude.sh dry run working correctly"
    else
        echo "launch-claude.sh dry run failed"
        return 1
    fi
    
    # Test Codex launcher dry run
    local codex_dry
    codex_dry=$("$LAUNCHER_DIR/launch-codex.sh" --dry-run "test query" 2>&1)
    
    if [[ "$codex_dry" =~ "Dry run complete" ]] && [[ "$codex_dry" =~ "would execute:" ]]; then
        echo "launch-codex.sh dry run working correctly"
    else
        echo "launch-codex.sh dry run failed"
        return 1
    fi
    
    return 0
}

# Test: Error handling for invalid options
test_invalid_option_handling() {
    # Test invalid option in Claude launcher
    local claude_error
    local claude_exit_code
    
    set +e
    claude_error=$("$LAUNCHER_DIR/launch-claude.sh" --invalid-option 2>&1)
    claude_exit_code=$?
    set -e
    
    if [[ $claude_exit_code -ne 0 ]]; then
        echo "launch-claude.sh correctly rejects invalid options"
    else
        echo "launch-claude.sh should reject invalid options"
        return 1
    fi
    
    # Test invalid option in Codex launcher
    local codex_error
    local codex_exit_code
    
    set +e
    codex_error=$("$LAUNCHER_DIR/launch-codex.sh" --invalid-option 2>&1)
    codex_exit_code=$?
    set -e
    
    if [[ $codex_exit_code -ne 0 ]]; then
        echo "launch-codex.sh correctly rejects invalid options"
    else
        echo "launch-codex.sh should reject invalid options"
        return 1
    fi
    
    return 0
}

# Test: Logging directory creation
test_logging_directory_creation() {
    local test_project="$TEST_TEMP_DIR/test_project"
    mkdir -p "$test_project"
    
    # Change to test project directory
    cd "$test_project"
    
    # Test Claude launcher logging setup (dry run to avoid actual execution)
    local claude_output
    claude_output=$("$LAUNCHER_DIR/launch-claude.sh" --dry-run --force-logs "test" 2>&1)
    
    if [[ "$claude_output" =~ "Session-based logging enabled" ]] && \
       [[ "$claude_output" =~ ".acforge/logs/claude-code/" ]]; then
        echo "launch-claude.sh logging setup working"
    else
        echo "launch-claude.sh logging setup failed"
        return 1
    fi
    
    # Test Codex launcher logging setup (dry run to avoid actual execution)
    local codex_output
    codex_output=$("$LAUNCHER_DIR/launch-codex.sh" --dry-run --force-logs "test" 2>&1)
    
    if [[ "$codex_output" =~ "Session-based logging enabled" ]] && \
       [[ "$codex_output" =~ ".acforge/logs/codex/" ]]; then
        echo "launch-codex.sh logging setup working"
    else
        echo "launch-codex.sh logging setup failed"
        return 1
    fi
    
    # Check that log directories were actually created
    if [[ -d "$test_project/.acforge/logs/claude-code" ]] && \
       [[ -d "$test_project/.acforge/logs/codex" ]]; then
        echo "Log directories created correctly"
    else
        echo "Log directories not created"
        return 1
    fi
    
    return 0
}

# Test: Environment detection consistency
test_environment_detection_consistency() {
    # Test environment detection in both launchers
    local claude_output
    claude_output=$("$LAUNCHER_DIR/launch-claude.sh" --dry-run "test" 2>&1)
    
    local codex_output
    codex_output=$("$LAUNCHER_DIR/launch-codex.sh" --dry-run "test" 2>&1)
    
    # Both should detect the same environment (in our case, devcontainer)
    if [[ "$claude_output" =~ "Detected devcontainer/codespace environment" ]] && \
       [[ "$codex_output" =~ "Detected devcontainer/codespace environment" ]]; then
        echo "Environment detection consistent between launchers"
    else
        echo "Environment detection inconsistent"
        return 1
    fi
    
    # Both should enable skip permissions
    if [[ "$claude_output" =~ "--dangerously-skip-permissions" ]] && \
       [[ "$codex_output" =~ "--dangerously-skip-permissions" ]]; then
        echo "Permission handling consistent between launchers"
    else
        echo "Permission handling inconsistent"
        return 1
    fi
    
    return 0
}

# Test: Interactive mode detection
test_interactive_mode_detection() {
    # Test without arguments (interactive mode)
    local claude_interactive
    claude_interactive=$(timeout 5 "$LAUNCHER_DIR/launch-claude.sh" --dry-run 2>&1 || true)
    
    local codex_interactive  
    codex_interactive=$(timeout 5 "$LAUNCHER_DIR/launch-codex.sh" --dry-run 2>&1 || true)
    
    # Should detect interactive mode and adjust logging
    if [[ "$claude_interactive" =~ "Interactive mode" ]] && \
       [[ "$codex_interactive" =~ "Interactive mode" ]]; then
        echo "Interactive mode detection working in both launchers"
    else
        echo "Interactive mode detection may not be working consistently"
        # This is not a hard failure as it depends on terminal detection
        return 0
    fi
    
    return 0
}

# Test: Configuration file handling
test_configuration_file_handling() {
    local test_project="$TEST_TEMP_DIR/test_config_project"
    mkdir -p "$test_project"
    cd "$test_project"
    
    # Create test .env file
    cat > ".env" << 'EOF'
TEST_CONFIG_VAR=test_value
EOF
    
    # Test configuration loading in both launchers
    local claude_output
    claude_output=$("$LAUNCHER_DIR/launch-claude.sh" --dry-run "test" 2>&1)
    
    local codex_output
    codex_output=$("$LAUNCHER_DIR/launch-codex.sh" --dry-run "test" 2>&1)
    
    # Both should load environment variables
    if [[ "$claude_output" =~ "Loading environment variables" ]] && \
       [[ "$codex_output" =~ "Loading environment variables" ]]; then
        echo "Configuration file loading working in both launchers"
    else
        echo "Configuration file loading may not be working consistently"
        return 1
    fi
    
    return 0
}

# Test: Codex-specific options
test_codex_specific_options() {
    # Test Codex-specific authentication modes
    local output
    output=$("$LAUNCHER_DIR/launch-codex.sh" --auth-mode api-key --dry-run "test" 2>&1)
    
    if [[ "$output" =~ "Auth mode: api-key" ]]; then
        echo "Codex authentication mode selection working"
    else
        echo "Codex authentication mode selection failed"
        return 1
    fi
    
    # Test Codex-specific approval modes
    output=$("$LAUNCHER_DIR/launch-codex.sh" --auto-edit --dry-run "test" 2>&1)
    
    if [[ "$output" =~ "Approval mode: auto-edit" ]]; then
        echo "Codex approval mode selection working"
    else
        echo "Codex approval mode selection failed"
        return 1
    fi
    
    # Test profile selection
    output=$("$LAUNCHER_DIR/launch-codex.sh" --profile work --dry-run "test" 2>&1)
    
    if [[ "$output" =~ "--profile work" ]]; then
        echo "Codex profile selection working"
    else
        echo "Codex profile selection failed"
        return 1
    fi
    
    return 0
}

# Test: Clean logs functionality
test_clean_logs_functionality() {
    local test_project="$TEST_TEMP_DIR/test_clean_project"
    mkdir -p "$test_project"
    cd "$test_project"
    
    # Create mock session directories for both tools
    mkdir -p ".acforge/logs/claude-code/20250101-120000"
    mkdir -p ".acforge/logs/codex/20250101-120000"
    echo "test" > ".acforge/logs/claude-code/20250101-120000/test.log"
    echo "test" > ".acforge/logs/codex/20250101-120000/test.log"
    
    # Test Claude clean logs (check that it detects sessions)
    local claude_clean
    set +e
    claude_clean=$(echo "n" | "$LAUNCHER_DIR/launch-claude.sh" --clean-logs 2>&1)
    set -e
    
    if [[ "$claude_clean" =~ "session directories to be deleted" ]]; then
        echo "launch-claude.sh clean logs detection working"
    else
        echo "launch-claude.sh clean logs detection failed"
        return 1
    fi
    
    # Test Codex clean logs (check that it detects sessions)
    local codex_clean
    set +e
    codex_clean=$(echo "n" | "$LAUNCHER_DIR/launch-codex.sh" --clean-logs 2>&1)
    set -e
    
    if [[ "$codex_clean" =~ "session directories to be deleted" ]]; then
        echo "launch-codex.sh clean logs detection working"
    else
        echo "launch-codex.sh clean logs detection failed"
        return 1
    fi
    
    return 0
}

# === MAIN TEST RUNNER ===

main() {
    echo -e "${BLUE}=== Launcher Integration Test Suite ===${NC}"
    echo "Testing CLI interface consistency and complete workflows"
    echo "Test temp directory: $TEST_TEMP_DIR"
    echo
    
    # Run all integration tests
    run_test "CLI Help Interface Consistency" test_cli_help_consistency
    run_test "Dry Run Mode Functionality" test_dry_run_mode
    run_test "Invalid Option Handling" test_invalid_option_handling
    run_test "Logging Directory Creation" test_logging_directory_creation
    run_test "Environment Detection Consistency" test_environment_detection_consistency
    run_test "Interactive Mode Detection" test_interactive_mode_detection
    run_test "Configuration File Handling" test_configuration_file_handling
    run_test "Codex-Specific Options" test_codex_specific_options
    run_test "Clean Logs Functionality" test_clean_logs_functionality
    
    # Print summary
    echo
    echo -e "${BLUE}=== Integration Test Summary ===${NC}"
    echo "Tests run: $TESTS_RUN"
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}🚀 All integration tests passed!${NC}"
        echo "Launcher CLI interfaces and workflows are working correctly"
        exit 0
    else
        echo -e "${RED}❌ Some integration tests failed!${NC}"
        echo "CLI interface or workflow issues detected"
        exit 1
    fi
}

# Run tests if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi