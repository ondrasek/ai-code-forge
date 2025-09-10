#!/bin/bash

# launcher-utils.sh - Shared utilities for AI launcher scripts
# Used by launch-claude.sh and launch-codex.sh for common functionality
# 
# This library provides:
# - Environment detection and auto-configuration
# - Secure .env file loading with validation
# - Session-based logging setup
# - Security validation functions
# - Common CLI patterns

set -euo pipefail

# Detect environment function - auto-detect devcontainer/codespace/docker environments
detect_environment() {
    local env_type="local"
    local skip_permissions="false"
    
    # Check for devcontainer environment or CI environment
    if [[ -n "${CODESPACES:-}" ]] || [[ -n "${REMOTE_CONTAINERS:-}" ]] || [[ -f "/.dockerenv" ]] || [[ -n "${DEVCONTAINER:-}" ]] || [[ -n "${GITHUB_ACTIONS:-}" ]] || [[ -n "${CI:-}" ]]; then
        echo "🔍 Detected devcontainer/codespace environment - enabling --dangerously-skip-permissions"
        env_type="container"
        skip_permissions="true"
    fi
    
    # Return values via global variables for calling script
    export DETECTED_ENV_TYPE="$env_type"
    export DETECTED_SKIP_PERMISSIONS="$skip_permissions"
}

# Secure .env file validation and parsing functions
validate_env_file() {
    local env_file="$1"

    # Check if file exists and is readable
    if [[ ! -f "$env_file" ]]; then
        return 1
    fi

    # Check file permissions - should not be world-readable for security
    if [[ -r "$env_file" ]]; then
        local perms
        perms=$(stat -c "%a" "$env_file" 2>/dev/null || stat -f "%OLp" "$env_file" 2>/dev/null || echo "644")
        if [[ "${perms: -1}" -gt 4 ]]; then
            echo "⚠️  Warning: $env_file is world-readable. Consider running: chmod 640 $env_file"
        fi
    fi

    # Check file size (prevent DoS via large files)
    local size
    size=$(wc -c < "$env_file" 2>/dev/null || echo 0)
    if [[ $size -gt 100000 ]]; then  # 100KB limit
        echo "❌ Error: $env_file is too large (${size} bytes). Maximum 100KB allowed." >&2
        return 1
    fi

    return 0
}

# Parse and load environment variables from .env file
load_env_file() {
    local env_file="$1"
    local debug_mode="${2:-false}"
    local loaded_count=0

    if ! validate_env_file "$env_file"; then
        return 1
    fi

    echo "🔧 Loading environment variables from $env_file"

    # Process file line by line with security validation
    local line_num=0
    while IFS= read -r line || [[ -n "$line" ]]; do
        ((line_num++))

        # Skip empty lines and comments
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue

        # Validate line format: KEY=VALUE
        if [[ "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)[[:space:]]*=[[:space:]]*(.*)[[:space:]]*$ ]]; then
            local key="${BASH_REMATCH[1]}"
            local value="${BASH_REMATCH[2]}"

            # Security checks
            # 1. Prevent command injection in values
            if [[ "$value" =~ \$\(|\`|\;|\||\& ]]; then
                echo "⚠️  Warning: Skipping potentially dangerous value for $key at line $line_num"
                continue
            fi

            # 2. Don't override existing environment variables (user environment takes precedence)
            if [[ -z "${!key:-}" ]]; then
                export "$key=$value"
                ((loaded_count++))

                # Mask sensitive values in debug output
                if [[ "$debug_mode" == "true" ]]; then
                    if [[ "$key" =~ (API_KEY|TOKEN|SECRET|PASSWORD|PASS) ]]; then
                        echo "   $key=***masked***"
                    else
                        echo "   $key=$value"
                    fi
                fi
            elif [[ "$debug_mode" == "true" ]]; then
                echo "   Skipped $key (already set in environment)"
            fi
        else
            echo "⚠️  Warning: Invalid format at line $line_num in $env_file: $line"
        fi
    done < "$env_file"

    if [[ $loaded_count -gt 0 ]]; then
        echo "✅ Loaded $loaded_count environment variables from $env_file"
    fi

    return 0
}

# Load configuration from multiple .env files with precedence
load_configuration() {
    local project_root="$1"
    local debug_mode="${2:-false}"
    local env_files=("${@:3}")  # Remaining arguments are env files
    local total_loaded=0
    local files_processed=0

    if [[ ${#env_files[@]} -eq 0 ]]; then
        # Default env files if none specified
        env_files=(".env" ".env.local" ".env.development")
    fi

    # Process .env files in reverse order so later files take precedence
    # (e.g., .env.local overrides .env, .env.development overrides both)
    for ((i=${#env_files[@]}-1; i>=0; i--)); do
        local env_file="${env_files[i]}"
        local full_path="$project_root/$env_file"
        if [[ -f "$full_path" ]]; then
            if load_env_file "$full_path" "$debug_mode"; then
                ((files_processed++))
            fi
        fi
    done

    if [[ $files_processed -eq 0 ]]; then
        if [[ "$debug_mode" == "true" ]]; then
            echo "ℹ️  No .env files found. Using system environment variables."
        fi
    fi
}

# Setup session-based logging system
setup_session_logging() {
    local tool_name="$1"          # "claude" or "codex"
    local project_root="$2"       # Project root directory
    local debug_mode="${3:-false}"
    local save_logs="${4:-true}"
    
    if [[ "$save_logs" != "true" ]]; then
        return 0
    fi
    
    # Generate session timestamp
    local session_timestamp
    session_timestamp=$(date +"%Y%m%d-%H%M%S")
    
    # Create tool-specific log base directory
    local log_base_dir="$project_root/.acforge/logs/$tool_name"
    local session_dir="$log_base_dir/$session_timestamp"
    mkdir -p "$session_dir"
    
    # Export session ID for MCP servers and other tools to use
    export "${tool_name^^}_SESSION_ID"="$session_timestamp"
    
    # Set up environment variables for comprehensive logging
    export CLAUDE_DEBUG=1
    export CLAUDE_CODE_ENABLE_TELEMETRY=1
    export ANTHROPIC_DEBUG=1
    export ANTHROPIC_LOG_LEVEL=debug
    export MCP_DEBUG=1
    export MCP_LOG_LEVEL=debug
    export MCP_TIMEOUT=30000
    
    # For Codex-specific logging
    if [[ "$tool_name" == "codex" ]]; then
        export RUST_LOG=debug
        export CODEX_DEBUG=1
        export OPENAI_LOG_LEVEL=debug
    fi
    
    # Disable OTEL exporters to prevent stdout pollution but enable telemetry collection
    export OTEL_LOGS_EXPORTER=""
    export OTEL_METRICS_EXPORTER=""
    export OTEL_TRACES_EXPORTER=""
    export OTEL_METRIC_EXPORT_INTERVAL=5000
    export OTEL_LOGS_EXPORT_INTERVAL=2000
    
    # Create session-specific log files with timestamps
    local session_log="$session_dir/session-$session_timestamp.log"
    local tool_log="$session_dir/$tool_name-$session_timestamp.log"
    local telemetry_log="$session_dir/telemetry-$session_timestamp.log"
    local debug_log="$session_dir/debug-$session_timestamp.log"
    local session_info="$session_dir/session-info-$session_timestamp.txt"
    
    # Store paths in tool-specific environment variables
    local tool_upper="${tool_name^^}"
    export "${tool_upper}_SESSION_LOG"="$session_log"
    export "${tool_upper}_TOOL_LOG"="$tool_log"
    export "${tool_upper}_TELEMETRY_LOG"="$telemetry_log"
    export "${tool_upper}_DEBUG_LOG"="$debug_log"
    export "${tool_upper}_SESSION_INFO"="$session_info"
    export "${tool_upper}_SESSION_DIR"="$session_dir"
    
    # Create session info file
    cat > "$session_info" << EOF
Tool: $tool_name
Session: $session_timestamp
Started: $(date)
Debug: $debug_mode
Project: $project_root
Session Directory: $session_dir
EOF
    
    echo "📝 Session-based logging enabled for $tool_name:"
    echo "   📁 Session directory: $session_dir"
    echo "   📋 Session log: $session_log"
    echo "   🔧 Tool log: $tool_log"
    echo "   📊 Telemetry log: $telemetry_log"
    echo "   🐛 Debug log: $debug_log"
    echo "   ℹ️  Session info: $session_info"
    echo "   🆔 Session ID: $session_timestamp"
    
    # Create empty log files to ensure they exist
    touch "$session_log" "$tool_log" "$telemetry_log" "$debug_log"
    
    if [[ "$debug_mode" == "true" ]]; then
        echo "🔧 Log files created and ready for writing"
        echo "   Environment variables set for enhanced logging"
    fi
}

# Find recent session directories for a tool
find_recent_sessions() {
    local tool_name="$1"
    local project_root="$2"
    local limit="${3:-5}"  # Default to 5 most recent sessions
    
    local log_base_dir="$project_root/.acforge/logs/$tool_name"
    
    if [[ ! -d "$log_base_dir" ]]; then
        return 1
    fi
    
    # Find session directories (format: YYYYMMDD-HHMMSS) and return them sorted by date
    find "$log_base_dir" -maxdepth 1 -type d -name "[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9][0-9]" 2>/dev/null | sort -r | head -"$limit"
}

# Clean all log files for a tool
clean_tool_logs() {
    local tool_name="$1"
    local project_root="$2"
    local interactive="${3:-true}"
    
    local log_base_dir="$project_root/.acforge/logs/$tool_name"
    
    echo "🧹 Cleaning all $tool_name session logs..."
    
    if [[ ! -d "$log_base_dir" ]]; then
        echo "ℹ️  No log directory found at $log_base_dir"
        return 0
    fi
    
    # Find all session directories (format: YYYYMMDD-HHMMSS)
    local session_dirs=($(find "$log_base_dir" -maxdepth 1 -type d -name "[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9][0-9]" 2>/dev/null | sort))
    
    if [[ ${#session_dirs[@]} -eq 0 ]]; then
        echo "ℹ️  No session directories found to delete."
        return 0
    fi
    
    # Count sessions and files to be deleted
    local total_files=0
    echo "📊 Session directories to be deleted:"
    for session_dir in "${session_dirs[@]}"; do
        local session_name=$(basename "$session_dir")
        local file_count=$(find "$session_dir" -type f 2>/dev/null | wc -l)
        total_files=$((total_files + file_count))
        echo "   📅 $session_name ($file_count files)"
    done
    echo "   📁 Total sessions: ${#session_dirs[@]}"
    echo "   📄 Total files: $total_files"
    echo
    
    # Confirm destructive action if interactive
    if [[ "$interactive" == "true" ]]; then
        echo "⚠️  This will permanently delete ALL session directories in:"
        echo "   📁 $log_base_dir"
        echo
        read -p "Are you sure you want to delete ${#session_dirs[@]} session directories with $total_files files? [y/N]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "❌ Log cleanup cancelled."
            return 1
        fi
    fi
    
    # Perform deletion with error handling
    local deleted_sessions=0
    local error_count=0
    
    for session_dir in "${session_dirs[@]}"; do
        local session_name=$(basename "$session_dir")
        echo "🗑️  Cleaning session $session_name..."
        
        if rm -rf "$session_dir" 2>/dev/null; then
            ((deleted_sessions++))
        else
            echo "❌ Failed to delete: $session_dir"
            ((error_count++))
        fi
    done
    
    echo
    if [[ $error_count -eq 0 ]]; then
        echo "✅ Successfully deleted $deleted_sessions session directories."
    else
        echo "⚠️  Deleted $deleted_sessions sessions with $error_count errors."
    fi
    
    # Keep the base directory - don't remove it even if empty
    # This preserves the logging structure for future sessions
}

# Comprehensive logging execution wrapper
execute_with_logging() {
    local cmd=("$@")
    local tool_name="${cmd[0]}"  # First argument should be the tool name
    local tool_upper="${tool_name^^}"
    
    # Get log file paths from environment variables set by setup_session_logging
    local session_log_var="${tool_upper}_SESSION_LOG"
    local tool_log_var="${tool_upper}_TOOL_LOG"
    local telemetry_log_var="${tool_upper}_TELEMETRY_LOG"
    local debug_log_var="${tool_upper}_DEBUG_LOG"
    
    local session_log="${!session_log_var:-}"
    local tool_log="${!tool_log_var:-}"
    local telemetry_log="${!telemetry_log_var:-}"
    local debug_log="${!debug_log_var:-}"
    
    if [[ -z "$session_log" ]]; then
        echo "❌ Error: Logging not initialized. Call setup_session_logging first."
        return 1
    fi
    
    # Write session header to all relevant logs
    local session_header
    session_header="=== $tool_name session started at $(date) ===
Command: ${cmd[*]}
=========================="
    
    # Write headers to organized log files
    echo "$session_header" >> "$session_log"
    echo "$session_header" >> "$debug_log"
    
    # Execute tool with comprehensive log redirection
    {
        # Capture all output and separate by patterns
        "${cmd[@]}" 2>&1 | while IFS= read -r line; do
            # Always output to terminal
            echo "$line"
            
            # Log to session and debug files
            echo "$line" >> "$session_log"
            echo "$line" >> "$debug_log"
            
            # Detect and separate tool-specific output
            case "$tool_name" in
                claude)
                    if [[ "$line" =~ [Mm][Cc][Pp]|server|tool ]]; then
                        echo "$line" >> "$tool_log"
                    fi
                    ;;
                codex)
                    if [[ "$line" =~ [Cc]odex|[Oo]penai|rust|cargo ]]; then
                        echo "$line" >> "$tool_log"
                    fi
                    ;;
            esac
            
            # Detect and separate telemetry output (broader patterns)
            if [[ "$line" =~ [Tt]elemetry|[Tt]race|[Ss]pan|[Mm]etric|otel|OTEL ]]; then
                echo "$line" >> "$telemetry_log"
            fi
        done
    }
    
    # Write session footer
    local session_footer="=== $tool_name session ended at $(date) ==="
    echo "$session_footer" >> "$session_log"
    echo "$session_footer" >> "$debug_log"
}

# Initialize paths for the calling script
init_paths() {
    local script_path="$1"
    
    # Calculate paths relative to the calling script
    local script_dir
    script_dir="$(cd "$(dirname "$script_path")" && pwd)"
    local project_root
    project_root="$(cd "$script_dir/.." && pwd)"
    
    # Export for use by calling scripts
    export SCRIPT_DIR="$script_dir"
    export PROJECT_ROOT="$project_root"
}

# Validate that required tools are available
validate_tool_requirements() {
    local tool_name="$1"
    shift
    local required_tools=("$@")
    
    local missing_tools=()
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        echo "❌ Error: Missing required tools for $tool_name:"
        for tool in "${missing_tools[@]}"; do
            echo "   - $tool"
        done
        echo
        echo "Please install missing tools and try again."
        return 1
    fi
    
    return 0
}

# Source guard to prevent execution when sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "❌ Error: launcher-utils.sh is a library and should not be executed directly."
    echo "Usage: source launcher-utils.sh"
    exit 1
fi