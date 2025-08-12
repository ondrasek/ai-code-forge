#!/bin/bash
set -euo pipefail

# Unit Tests for Launcher Utilities Core Functions
# Tests individual functions for correctness and edge case handling
# Usage: ./test-launcher-units.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAUNCHER_DIR="$(dirname "$SCRIPT_DIR")"
LIB_DIR="$LAUNCHER_DIR/lib"

# Source the launcher utilities to test
if [[ ! -f "$LIB_DIR/launcher-utils.sh" ]]; then
    echo "❌ Error: launcher-utils.sh not found at $LIB_DIR/launcher-utils.sh"
    exit 1
fi

source "$LIB_DIR/launcher-utils.sh"

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
TEST_TEMP_DIR="/tmp/launcher-units-test-$$"
mkdir -p "$TEST_TEMP_DIR"

# Cleanup function
cleanup() {
    rm -rf "$TEST_TEMP_DIR" 2>/dev/null || true
    # Clean up any environment variables set during tests
    unset CODESPACES REMOTE_CONTAINERS DEVCONTAINER 2>/dev/null || true
    unset DETECTED_ENV_TYPE DETECTED_SKIP_PERMISSIONS 2>/dev/null || true
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

# === UNIT TESTS ===

# Test: detect_environment function with different scenarios
test_detect_environment_scenarios() {
    # Save original environment
    local orig_codespaces="${CODESPACES:-}"
    local orig_remote="${REMOTE_CONTAINERS:-}"
    local orig_devcontainer="${DEVCONTAINER:-}"
    
    # Clear environment first
    unset CODESPACES REMOTE_CONTAINERS DEVCONTAINER 2>/dev/null || true
    
    # Test 1: Local environment (no container variables)
    detect_environment
    if [[ "${DETECTED_ENV_TYPE}" == "local" ]] && [[ "${DETECTED_SKIP_PERMISSIONS}" == "false" ]]; then
        echo "Local environment detected correctly"
    else
        echo "Local environment detection failed: type=${DETECTED_ENV_TYPE}, skip=${DETECTED_SKIP_PERMISSIONS}"
        return 1
    fi
    
    # Test 2: Codespaces environment
    export CODESPACES="true"
    detect_environment
    if [[ "${DETECTED_ENV_TYPE}" == "container" ]] && [[ "${DETECTED_SKIP_PERMISSIONS}" == "true" ]]; then
        echo "Codespaces environment detected correctly"
    else
        echo "Codespaces detection failed: type=${DETECTED_ENV_TYPE}, skip=${DETECTED_SKIP_PERMISSIONS}"
        return 1
    fi
    
    # Test 3: Remote containers environment
    unset CODESPACES
    export REMOTE_CONTAINERS="true"
    detect_environment
    if [[ "${DETECTED_ENV_TYPE}" == "container" ]] && [[ "${DETECTED_SKIP_PERMISSIONS}" == "true" ]]; then
        echo "Remote containers environment detected correctly"
    else
        echo "Remote containers detection failed: type=${DETECTED_ENV_TYPE}, skip=${DETECTED_SKIP_PERMISSIONS}"
        return 1
    fi
    
    # Test 4: Devcontainer environment
    unset REMOTE_CONTAINERS
    export DEVCONTAINER="true"
    detect_environment
    if [[ "${DETECTED_ENV_TYPE}" == "container" ]] && [[ "${DETECTED_SKIP_PERMISSIONS}" == "true" ]]; then
        echo "Devcontainer environment detected correctly"
    else
        echo "Devcontainer detection failed: type=${DETECTED_ENV_TYPE}, skip=${DETECTED_SKIP_PERMISSIONS}"
        return 1
    fi
    
    # Restore original environment
    unset CODESPACES REMOTE_CONTAINERS DEVCONTAINER
    if [[ -n "$orig_codespaces" ]]; then export CODESPACES="$orig_codespaces"; fi
    if [[ -n "$orig_remote" ]]; then export REMOTE_CONTAINERS="$orig_remote"; fi
    if [[ -n "$orig_devcontainer" ]]; then export DEVCONTAINER="$orig_devcontainer"; fi
    
    return 0
}

# Test: init_paths function
test_init_paths_function() {
    local test_script="$TEST_TEMP_DIR/test-script.sh"
    echo "#!/bin/bash" > "$test_script"
    
    # Save original values
    local orig_script_dir="${SCRIPT_DIR:-}"
    local orig_project_root="${PROJECT_ROOT:-}"
    
    # Test init_paths
    init_paths "$test_script"
    
    if [[ -n "${SCRIPT_DIR}" ]] && [[ -n "${PROJECT_ROOT}" ]]; then
        if [[ "${SCRIPT_DIR}" == "$TEST_TEMP_DIR" ]]; then
            echo "init_paths sets SCRIPT_DIR correctly"
        else
            echo "SCRIPT_DIR incorrect: expected $TEST_TEMP_DIR, got ${SCRIPT_DIR}"
            return 1
        fi
        
        # PROJECT_ROOT should be parent of SCRIPT_DIR
        local expected_project_root
        expected_project_root="$(dirname "$TEST_TEMP_DIR")"
        if [[ "${PROJECT_ROOT}" == "$expected_project_root" ]]; then
            echo "init_paths sets PROJECT_ROOT correctly"
        else
            echo "PROJECT_ROOT incorrect: expected $expected_project_root, got ${PROJECT_ROOT}"
            return 1
        fi
    else
        echo "init_paths failed to set environment variables"
        return 1
    fi
    
    # Restore original values
    export SCRIPT_DIR="$orig_script_dir"
    export PROJECT_ROOT="$orig_project_root"
    
    return 0
}

# Test: validate_tool_requirements function
test_validate_tool_requirements() {
    # Test with existing tool (bash should exist)
    if validate_tool_requirements "test-tool" "bash" >/dev/null 2>&1; then
        echo "validate_tool_requirements correctly accepts existing tool"
    else
        echo "validate_tool_requirements incorrectly rejects existing tool (bash)"
        return 1
    fi
    
    # Test with non-existing tool
    if ! validate_tool_requirements "test-tool" "nonexistent-impossible-tool-12345" >/dev/null 2>&1; then
        echo "validate_tool_requirements correctly rejects non-existing tool"
    else
        echo "validate_tool_requirements incorrectly accepts non-existing tool"
        return 1
    fi
    
    # Test with multiple tools (mix of existing and non-existing)
    if ! validate_tool_requirements "test-tool" "bash" "nonexistent-tool" >/dev/null 2>&1; then
        echo "validate_tool_requirements correctly rejects when some tools missing"
    else
        echo "validate_tool_requirements should reject when any tool is missing"
        return 1
    fi
    
    return 0
}

# Test: load_configuration function
test_load_configuration() {
    local test_project="$TEST_TEMP_DIR/test_project"
    mkdir -p "$test_project"
    
    # Create test .env file
    cat > "$test_project/.env" << 'EOF'
# Test configuration
TEST_VAR1=value1
TEST_VAR2=value2
# Comment line
TEST_VAR3=value3

EOF
    
    # Create .env.local file (should override .env)
    cat > "$test_project/.env.local" << 'EOF'
TEST_VAR2=overridden_value
TEST_VAR4=local_value
EOF
    
    # Save original environment
    local orig_test_var1="${TEST_VAR1:-}"
    local orig_test_var2="${TEST_VAR2:-}"
    local orig_test_var3="${TEST_VAR3:-}"
    local orig_test_var4="${TEST_VAR4:-}"
    
    # Clear test variables
    unset TEST_VAR1 TEST_VAR2 TEST_VAR3 TEST_VAR4 2>/dev/null || true
    
    # Load configuration
    load_configuration "$test_project" false
    
    # Check loaded values
    if [[ "${TEST_VAR1:-}" == "value1" ]] && \
       [[ "${TEST_VAR2:-}" == "overridden_value" ]] && \
       [[ "${TEST_VAR3:-}" == "value3" ]] && \
       [[ "${TEST_VAR4:-}" == "local_value" ]]; then
        echo "load_configuration works correctly with precedence"
    else
        echo "load_configuration failed: VAR1=${TEST_VAR1:-}, VAR2=${TEST_VAR2:-}, VAR3=${TEST_VAR3:-}, VAR4=${TEST_VAR4:-}"
        return 1
    fi
    
    # Restore original environment
    if [[ -n "$orig_test_var1" ]]; then export TEST_VAR1="$orig_test_var1"; else unset TEST_VAR1 2>/dev/null || true; fi
    if [[ -n "$orig_test_var2" ]]; then export TEST_VAR2="$orig_test_var2"; else unset TEST_VAR2 2>/dev/null || true; fi
    if [[ -n "$orig_test_var3" ]]; then export TEST_VAR3="$orig_test_var3"; else unset TEST_VAR3 2>/dev/null || true; fi
    if [[ -n "$orig_test_var4" ]]; then export TEST_VAR4="$orig_test_var4"; else unset TEST_VAR4 2>/dev/null || true; fi
    
    return 0
}

# Test: find_recent_sessions function
test_find_recent_sessions() {
    local test_project="$TEST_TEMP_DIR/test_project"
    local log_base="$test_project/.acf/logs/test-tool"
    mkdir -p "$log_base"
    
    # Create mock session directories with timestamps
    local sessions=("20250101-120000" "20250102-130000" "20250103-140000" "20250104-150000")
    for session in "${sessions[@]}"; do
        mkdir -p "$log_base/$session"
        echo "test" > "$log_base/$session/test.log"
    done
    
    # Test finding recent sessions
    local found_sessions
    found_sessions=($(find_recent_sessions "test-tool" "$test_project" 3))
    
    if [[ ${#found_sessions[@]} -eq 3 ]]; then
        # Should return most recent 3 in reverse chronological order
        if [[ "$(basename "${found_sessions[0]}")" == "20250104-150000" ]] && \
           [[ "$(basename "${found_sessions[1]}")" == "20250103-140000" ]] && \
           [[ "$(basename "${found_sessions[2]}")" == "20250102-130000" ]]; then
            echo "find_recent_sessions returns correct sessions in correct order"
        else
            echo "find_recent_sessions order incorrect: ${found_sessions[*]}"
            return 1
        fi
    else
        echo "find_recent_sessions returned wrong count: ${#found_sessions[@]} (expected 3)"
        return 1
    fi
    
    # Test with tool that has no sessions
    local empty_sessions
    empty_sessions=($(find_recent_sessions "nonexistent-tool" "$test_project" 5 2>/dev/null || true))
    
    if [[ ${#empty_sessions[@]} -eq 0 ]]; then
        echo "find_recent_sessions correctly handles non-existent tool"
    else
        echo "find_recent_sessions should return empty for non-existent tool"
        return 1
    fi
    
    return 0
}

# Test: session logging environment variable setup
test_session_logging_env_vars() {
    local test_project="$TEST_TEMP_DIR/test_project"
    mkdir -p "$test_project"
    
    # Test session logging setup
    setup_session_logging "testool" "$test_project" false true >/dev/null 2>&1
    
    # Check environment variables are set
    if [[ -n "${TESTOOL_SESSION_ID:-}" ]] && \
       [[ -n "${TESTOOL_SESSION_LOG:-}" ]] && \
       [[ -n "${TESTOOL_TOOL_LOG:-}" ]] && \
       [[ -n "${TESTOOL_TELEMETRY_LOG:-}" ]] && \
       [[ -n "${TESTOOL_DEBUG_LOG:-}" ]] && \
       [[ -n "${TESTOOL_SESSION_INFO:-}" ]] && \
       [[ -n "${TESTOOL_SESSION_DIR:-}" ]]; then
        echo "Session logging environment variables set correctly"
    else
        echo "Session logging failed to set environment variables"
        return 1
    fi
    
    # Check session ID format (should be YYYYMMDD-HHMMSS)
    if [[ "${TESTOOL_SESSION_ID}" =~ ^[0-9]{8}-[0-9]{6}$ ]]; then
        echo "Session ID format is correct"
    else
        echo "Session ID format incorrect: ${TESTOOL_SESSION_ID}"
        return 1
    fi
    
    # Check that log files exist
    if [[ -f "${TESTOOL_SESSION_LOG}" ]] && \
       [[ -f "${TESTOOL_TOOL_LOG}" ]] && \
       [[ -f "${TESTOOL_TELEMETRY_LOG}" ]] && \
       [[ -f "${TESTOOL_DEBUG_LOG}" ]] && \
       [[ -f "${TESTOOL_SESSION_INFO}" ]]; then
        echo "Log files created successfully"
    else
        echo "Log files not created properly"
        return 1
    fi
    
    return 0
}

# Test: clean_tool_logs function (non-interactive mode)
test_clean_tool_logs() {
    local test_project="$TEST_TEMP_DIR/test_project"
    local log_base="$test_project/.acf/logs/cleantest"
    mkdir -p "$log_base"
    
    # Create mock session directories
    local sessions=("20250101-120000" "20250102-130000")
    for session in "${sessions[@]}"; do
        mkdir -p "$log_base/$session"
        echo "test log content" > "$log_base/$session/test.log"
        echo "more content" > "$log_base/$session/other.log"
    done
    
    # Test non-interactive cleanup
    clean_tool_logs "cleantest" "$test_project" false >/dev/null 2>&1
    
    # Check that sessions were deleted
    if [[ ! -d "$log_base/20250101-120000" ]] && [[ ! -d "$log_base/20250102-130000" ]]; then
        echo "clean_tool_logs successfully removed session directories"
    else
        echo "clean_tool_logs failed to remove session directories"
        return 1
    fi
    
    # Base directory should still exist (empty)
    if [[ -d "$log_base" ]]; then
        echo "Log base directory preserved correctly"
    else
        echo "Log base directory should be preserved"
        return 1
    fi
    
    return 0
}

# Test: Environment variable masking in debug mode
test_env_var_masking() {
    local test_env="$TEST_TEMP_DIR/test_masking.env"
    
    cat > "$test_env" << 'EOF'
NORMAL_VAR=normal_value
API_KEY=secret_key_value
TOKEN=secret_token_value  
SECRET=very_secret_value
PASSWORD=secret_password
PASSPHRASE=secret_phrase
REGULAR_VAR=another_normal_value
EOF

    # Clear any existing test variables
    unset NORMAL_VAR API_KEY TOKEN SECRET PASSWORD PASSPHRASE REGULAR_VAR 2>/dev/null || true
    
    # Load with debug mode enabled
    local output
    output=$(load_env_file "$test_env" true 2>&1)
    
    # Check that sensitive values are masked
    if [[ "$output" =~ "API_KEY=***masked***" ]] && \
       [[ "$output" =~ "TOKEN=***masked***" ]] && \
       [[ "$output" =~ "SECRET=***masked***" ]] && \
       [[ "$output" =~ "PASSWORD=***masked***" ]]; then
        echo "Sensitive environment variables are properly masked"
    else
        echo "Environment variable masking failed"
        return 1
    fi
    
    # Check that normal values are shown
    if [[ "$output" =~ "NORMAL_VAR=normal_value" ]] && \
       [[ "$output" =~ "REGULAR_VAR=another_normal_value" ]]; then
        echo "Normal environment variables are shown correctly"
    else
        echo "Normal environment variables not displayed correctly"
        return 1
    fi
    
    # Verify variables were actually loaded
    if [[ "${API_KEY:-}" == "secret_key_value" ]] && \
       [[ "${NORMAL_VAR:-}" == "normal_value" ]]; then
        echo "Environment variables loaded correctly despite masking"
    else
        echo "Environment variables not loaded properly"
        return 1
    fi
    
    return 0
}

# === MAIN TEST RUNNER ===

main() {
    echo -e "${BLUE}=== Launcher Utilities Unit Test Suite ===${NC}"
    echo "Testing individual functions for correctness and edge cases"
    echo "Test temp directory: $TEST_TEMP_DIR"
    echo
    
    # Run all unit tests
    run_test "Environment Detection Scenarios" test_detect_environment_scenarios
    run_test "Path Initialization" test_init_paths_function
    run_test "Tool Requirements Validation" test_validate_tool_requirements
    run_test "Configuration Loading" test_load_configuration
    run_test "Recent Sessions Finding" test_find_recent_sessions
    run_test "Session Logging Environment Setup" test_session_logging_env_vars
    run_test "Tool Logs Cleanup" test_clean_tool_logs
    run_test "Environment Variable Masking" test_env_var_masking
    
    # Print summary
    echo
    echo -e "${BLUE}=== Unit Test Summary ===${NC}"
    echo "Tests run: $TESTS_RUN"
    echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}🎯 All unit tests passed!${NC}"
        echo "Launcher utilities core functions are working correctly"
        exit 0
    else
        echo -e "${RED}❌ Some unit tests failed!${NC}"
        echo "Core functionality issues detected in launcher utilities"
        exit 1
    fi
}

# Run tests if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi