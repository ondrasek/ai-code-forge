# Shell/Bash Stack Instructions

MANDATORY operational instructions for Claude Code when working with shell/bash scripts.

## Error Handling - NO EXCEPTIONS

**MANDATORY: Use strict error handling** - ALWAYS include at script start.

```bash
#!/bin/bash
set -euo pipefail  # Exit on error, undefined vars, pipe failures
```

**MANDATORY: Proper signal handling and cleanup:**
```bash
cleanup() {
    local exit_code=$?
    echo "Cleaning up..." >&2
    
    # Kill child processes
    for pid in "${CHILD_PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    
    # Remove temp files
    [[ -n "${TEMP_DIR:-}" ]] && rm -rf "$TEMP_DIR"
    exit $exit_code
}

trap cleanup EXIT
trap 'cleanup; exit 130' INT
trap 'cleanup; exit 143' TERM
```

## Variable Handling - ENFORCE

**MANDATORY: Always quote variables and use parameter expansion:**
```bash
# Correct - always quote
echo "$variable"
cp "$source_file" "$destination_dir"

# Correct - parameter expansion with defaults
CONFIG_FILE="${CONFIG_FILE:-config.json}"
TIMEOUT="${TIMEOUT:-30}"

# Correct - validate required variables
: "${REQUIRED_VAR:?REQUIRED_VAR must be set}"
```

## Input Validation - SECURITY CRITICAL

**CRITICAL: Validate all inputs to prevent injection attacks:**
```bash
validate_input() {
    local input="$1"
    
    # Prevent path traversal
    if [[ "$input" == *".."* ]] || [[ "$input" =~ ^/ ]]; then
        echo "ERROR: Invalid input contains unsafe characters" >&2
        return 1
    fi
    
    # Whitelist allowed characters
    if [[ ! "$input" =~ ^[a-zA-Z0-9._/-]+$ ]]; then
        echo "ERROR: Invalid characters in input" >&2
        return 1
    fi
    
    # Length validation
    if [[ ${#input} -gt 100 ]]; then
        echo "ERROR: Input too long" >&2
        return 1
    fi
    
    return 0
}

# Prevent command injection
safe_execute() {
    local cmd="$1"
    shift
    local -a args=("$@")
    
    # Validate command exists
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "ERROR: Command not found: $cmd" >&2
        return 1
    fi
    
    # Validate arguments
    for arg in "${args[@]}"; do
        validate_input "$arg" || return 1
    done
    
    # Execute safely
    "$cmd" "${args[@]}"
}
```

## CLI Argument Parsing - REQUIRED

**REQUIRED: Use robust argument parsing pattern:**
```bash
show_help() {
    cat << 'EOF'
Usage: script.sh [OPTIONS] [ARGUMENTS]
OPTIONS:
    -h, --help          Show help
    -v, --verbose       Verbose output
    -f, --file FILE     Input file
    --dry-run          Show what would be executed
EOF
}

parse_args() {
    POSITIONAL_ARGS=()
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verbose)
                VERBOSE="true"
                shift
                ;;
            -f|--file)
                if [[ -z "$2" ]] || [[ "$2" =~ ^- ]]; then
                    echo "ERROR: --file requires an argument" >&2
                    exit 1
                fi
                INPUT_FILE="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN="true"
                shift
                ;;
            -*)
                echo "ERROR: Unknown option $1" >&2
                exit 1
                ;;
            *)
                POSITIONAL_ARGS+=("$1")
                shift
                ;;
        esac
    done
}
```

## Cross-Platform Compatibility - ENFORCE

**ENFORCE: Use portable patterns:**
```bash
# Portable directory detection
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Portable stat command
get_file_perms() {
    local file="$1"
    stat -c "%a" "$file" 2>/dev/null || stat -f "%A" "$file" 2>/dev/null
}

# Feature detection not OS detection
if command -v greadlink >/dev/null 2>&1; then
    READLINK="greadlink"
else
    READLINK="readlink"
fi
```

## Environment Variables - SECURITY CRITICAL

**CRITICAL: Secure environment variable handling:**
```bash
validate_env_file() {
    local env_file="$1"
    
    [[ -f "$env_file" ]] || return 1
    
    # Check permissions - should not be world-readable
    local perms
    perms=$(get_file_perms "$env_file")
    if [[ "${perms: -1}" -gt 4 ]]; then
        echo "WARNING: $env_file is world-readable" >&2
    fi
    
    # Check file size (prevent DoS)
    local size
    size=$(wc -c < "$env_file" 2>/dev/null || echo 0)
    if [[ $size -gt 100000 ]]; then
        echo "ERROR: $env_file too large (${size} bytes)" >&2
        return 1
    fi
    
    return 0
}

load_env_file() {
    local env_file="$1"
    validate_env_file "$env_file" || return 1
    
    while IFS= read -r line || [[ -n "$line" ]]; do
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
        
        if [[ "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)[[:space:]]*=[[:space:]]*(.*)[[:space:]]*$ ]]; then
            local key="${BASH_REMATCH[1]}"
            local value="${BASH_REMATCH[2]}"
            
            # Prevent command injection in values
            if [[ "$value" =~ \$\(|\`|\;|\||\& ]]; then
                echo "WARNING: Skipping dangerous value for $key" >&2
                continue
            fi
            
            # Don't override existing environment
            if [[ -z "${!key:-}" ]]; then
                export "$key=$value"
            fi
        fi
    done < "$env_file"
}
```

## Logging System - MANDATORY

**MANDATORY: Comprehensive logging:**
```bash
# Global logging configuration
LOG_LEVEL="${LOG_LEVEL:-INFO}"
LOG_FILE="${LOG_FILE:-}"
SESSION_ID="$(date +"%Y%m%d-%H%M%S")"

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    local log_line="[$timestamp] [$level] [$SESSION_ID] $message"
    
    case "$level" in
        WARN|ERROR)
            echo "$log_line" >&2
            ;;
        *)
            echo "$log_line"
            ;;
    esac
    
    if [[ -n "$LOG_FILE" ]]; then
        echo "$log_line" >> "$LOG_FILE"
    fi
}

log_debug() { [[ "$LOG_LEVEL" == "DEBUG" ]] && log "DEBUG" "$@"; }
log_info()  { log "INFO" "$@"; }
log_warn()  { log "WARN" "$@"; }
log_error() { log "ERROR" "$@"; }

# Mask sensitive information
log_sensitive() {
    local level="$1"
    local key="$2"
    local value="$3"
    
    if [[ "$key" =~ (API_KEY|TOKEN|SECRET|PASSWORD|PASS) ]]; then
        log "$level" "$key=***masked***"
    else
        log "$level" "$key=$value"
    fi
}
```

## Process Management - REQUIRED

**REQUIRED: Track and manage child processes:**
```bash
# Process tracking
declare -a CHILD_PIDS=()

spawn_process() {
    local cmd="$1"
    shift
    
    "$cmd" "$@" &
    local pid=$!
    CHILD_PIDS+=("$pid")
    log_debug "Spawned process: $cmd (PID: $pid)"
    echo "$pid"
}

wait_for_processes() {
    for pid in "${CHILD_PIDS[@]}"; do
        if wait "$pid"; then
            log_debug "Process $pid completed successfully"
        else
            log_error "Process $pid failed with exit code $?"
        fi
    done
}
```

## Configuration File Handling - ENFORCE

**ENFORCE: Secure config file parsing:**
```bash
parse_json_config() {
    local config_file="$1"
    
    if ! command -v jq >/dev/null 2>&1; then
        log_error "jq is required for JSON parsing"
        return 1
    fi
    
    # Validate JSON structure
    if ! jq empty "$config_file" 2>/dev/null; then
        log_error "Invalid JSON in $config_file"
        return 1
    fi
    
    # Extract values safely
    API_KEY=$(jq -r '.api_key // ""' "$config_file")
    TIMEOUT=$(jq -r '.timeout // 30' "$config_file")
}

parse_yaml_config() {
    local config_file="$1"
    
    if ! command -v yq >/dev/null 2>&1; then
        log_error "yq is required for YAML parsing"
        return 1
    fi
    
    if ! yq eval '.' "$config_file" >/dev/null 2>&1; then
        log_error "Invalid YAML in $config_file"
        return 1
    fi
    
    DATABASE_URL=$(yq eval '.database.url // ""' "$config_file")
}
```

## Testing Structure - REQUIRED

**REQUIRED: Make scripts testable:**
```bash
#!/bin/bash

# Source guard for testing
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    SCRIPT_MODE="execute"
else
    SCRIPT_MODE="source"
fi

# Main function for testability
main() {
    parse_args "$@"
    validate_environment
    execute_workflow
}

# Only run if executed directly
if [[ "$SCRIPT_MODE" == "execute" ]]; then
    main "$@"
fi

# Test functions available when sourced
test_argument_parsing() {
    local original_args=("$@")
    set -- --verbose --file test.txt
    parse_args "$@"
    set -- "${original_args[@]}"  # Restore
    
    [[ "$VERBOSE" == "true" ]] || return 1
    [[ "$INPUT_FILE" == "test.txt" ]] || return 1
}

run_tests() {
    test_argument_parsing
    test_input_validation
    test_configuration_loading
}
```

## Integration Patterns - MANDATORY

**MANDATORY: Safe external tool integration:**
```bash
check_dependencies() {
    local -a required_tools=("jq" "curl" "git")
    local missing_tools=()
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing_tools+=("$tool")
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        return 1
    fi
}

api_call() {
    local url="$1"
    local method="${2:-GET}"
    local max_retries=3
    local retry_count=0
    
    while [[ $retry_count -lt $max_retries ]]; do
        local response
        response=$(curl -s -w "%{http_code}" -X "$method" "$url")
        
        local http_code="${response: -3}"
        response="${response%???}"
        
        case "$http_code" in
            200|201|204)
                echo "$response"
                return 0
                ;;
            5*)
                log_warn "Server error ($http_code), retrying..."
                ;;
            *)
                log_error "API call failed with status $http_code"
                return 1
                ;;
        esac
        
        ((retry_count++))
        sleep $((retry_count * 2))
    done
    
    return 1
}
```

## Required Structure - ENFORCE

**MANDATORY structure for shell scripts:**
```bash
#!/bin/bash
set -euo pipefail

# Script metadata
declare -r SCRIPT_VERSION="1.0.0"
declare -r SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Configuration with defaults
declare -g VERBOSE="${VERBOSE:-false}"
declare -g DRY_RUN="${DRY_RUN:-false}"
declare -g LOG_LEVEL="${LOG_LEVEL:-INFO}"

# Process tracking
declare -a CHILD_PIDS=()

# Functions: logging, validation, parsing, execution
# Signal handlers: cleanup
# Main function: orchestration
# Conditional execution: source guard

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
```