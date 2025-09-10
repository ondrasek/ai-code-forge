#!/bin/bash

# launch-claude - Enhanced Claude Code wrapper with custom configuration
# Usage: launch-claude [options] [query]
#
# This script provides a custom wrapper around claude with:
# - Enhanced defaults with logging enabled
# - Default model set to sonnet
# - Custom master prompt loading
# - Enhanced verbose logging capabilities
# - MCP server verbose logging
# - Auto-detection of devcontainer/codespace environments

set -euo pipefail

# Set Node.js memory options to prevent out of memory crashes
export NODE_OPTIONS="--max-old-space-size=4096"

# Configuration variables
DEFAULT_MODEL="sonnet"
MASTER_PROMPT_FILE=".support/prompts/master-prompt.md"
VERBOSE_MODE="true"
DEBUG_MODE="true"
MCP_DEBUG="true"
LOG_FILE=""
SAVE_LOGS="true"
SKIP_PERMISSIONS="false"
USE_CONTINUE="true"
USE_RESUME="false"
RESUME_SESSION_ID=""
DRY_RUN="false"

# Environment file configuration
ENV_FILES=(".env" ".env.local" ".env.development")
LOAD_ENV="true"

# Log directory configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_BASE_DIR="$PROJECT_ROOT/.acforge/logs/claude-code"

# Auto-detect environment function
detect_environment() {
    # Check for devcontainer environment or CI environment
    if [[ -n "${CODESPACES:-}" ]] || [[ -n "${REMOTE_CONTAINERS:-}" ]] || [[ -f "/.dockerenv" ]] || [[ -n "${DEVCONTAINER:-}" ]] || [[ -n "${GITHUB_ACTIONS:-}" ]] || [[ -n "${CI:-}" ]]; then
        echo "🔍 Detected devcontainer/codespace environment - enabling --dangerously-skip-permissions"
        SKIP_PERMISSIONS="true"
    fi
}

# Detect existing Claude Code conversations for the current project
detect_conversations() {
    local project_path="$1"
    
    # Convert project path to Claude Code project name format
    # Claude Code uses the workspace path with slashes replaced by dashes, leading slash removed
    local project_name=$(echo "$project_path" | sed 's|/|-|g' | sed 's|^-||')
    local claude_projects_dir="$HOME/.claude/projects/$project_name"
    
    if [[ "$DEBUG_MODE" == "true" ]]; then
        echo "🔍 Checking for conversations in: $claude_projects_dir" >&2
    fi
    
    # Check if Claude projects directory exists
    if [[ -d "$claude_projects_dir" ]]; then
        # Find conversation files (*.jsonl)
        local conversation_files=()
        while IFS= read -r -d '' file; do
            conversation_files+=("$file")
        done < <(find "$claude_projects_dir" -name "*.jsonl" -type f -print0 2>/dev/null)
        
        if [[ ${#conversation_files[@]} -gt 0 ]]; then
            if [[ "$DEBUG_MODE" == "true" ]]; then
                echo "🔍 Found ${#conversation_files[@]} conversation(s)" >&2
            fi
            return 0  # Conversations found
        else
            if [[ "$DEBUG_MODE" == "true" ]]; then
                echo "🔍 No conversation files found in project directory" >&2
            fi
        fi
    else
        if [[ "$DEBUG_MODE" == "true" ]]; then
            echo "🔍 No Claude projects directory found for this project" >&2
        fi
    fi
    
    return 1  # No conversations found
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
        perms=$(stat -c "%a" "$env_file" 2>/dev/null || stat -f "%A" "$env_file" 2>/dev/null)
        if [[ "${perms: -1}" -gt 4 ]]; then
            echo "⚠️  Warning: $env_file is world-readable. Consider running: chmod 640 $env_file"
        fi
    fi

    # Check file size (prevent DoS via large files)
    local size
    size=$(wc -c < "$env_file" 2>/dev/null || echo 0)
    if [[ $size -gt 100000 ]]; then  # 100KB limit
        echo "❌ Error: $env_file is too large (${size} bytes). Maximum 100KB allowed."
        return 1
    fi

    return 0
}

# Parse and load environment variables from .env file
load_env_file() {
    local env_file="$1"
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
                if [[ "$DEBUG_MODE" == "true" ]]; then
                    if [[ "$key" =~ (API_KEY|TOKEN|SECRET|PASSWORD|PASS) ]]; then
                        echo "   $key=***masked***"
                    else
                        echo "   $key=$value"
                    fi
                fi
            elif [[ "$DEBUG_MODE" == "true" ]]; then
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
    if [[ "$LOAD_ENV" != "true" ]]; then
        return 0
    fi

    local total_loaded=0
    local files_processed=0

    # Process .env files in order of precedence (.env.development overrides .env, etc.)
    for env_file in "${ENV_FILES[@]}"; do
        local full_path="$PROJECT_ROOT/$env_file"
        if [[ -f "$full_path" ]]; then
            if load_env_file "$full_path"; then
                ((files_processed++))
            fi
        fi
    done

    if [[ $files_processed -eq 0 ]]; then
        if [[ "$DEBUG_MODE" == "true" ]]; then
            echo "ℹ️  No .env files found. Using system environment variables."
        fi
    fi
}

# Help function
show_help() {
    cat << EOF
launch-claude - Enhanced Claude Code wrapper

USAGE:
    launch-claude [OPTIONS] [QUERY]

OPTIONS:
    -h, --help                Show this help message
    -q, --quiet              Disable verbose mode (overrides default enable)
    --no-debug               Disable debug mode (overrides default enable)
    --no-mcp-debug           Disable MCP server debug logging (overrides default enable)
    --no-logs                Disable log saving (overrides default enable)
    --force-logs             Force enable logging even in interactive mode
    -m, --model MODEL        Set model (default: $DEFAULT_MODEL)
    --log-file FILE          Save logs to specified file (default: timestamped)
    -c, --continue           Continue the most recent conversation (default: enabled)
    --no-continue            Disable continue mode (start new conversation)
    -r, --resume [ID]        Resume a conversation (with optional session ID)
    --dry-run                Show what would be executed without running
    --analyze-logs           Analyze existing log files using Claude Code agents
    --clean-logs             Remove all existing session directories from .acforge/logs/
    --troubleshoot-mcp       Analyze and troubleshoot MCP server issues using agents
    --skip-permissions       Force enable --dangerously-skip-permissions flag
    --no-skip-permissions    Force disable --dangerously-skip-permissions flag
    --no-env                 Disable .env file loading
    --env-file FILE          Load specific .env file (can be used multiple times)

EXAMPLES:
    launch-claude "Review my code"                    # Continue most recent conversation
    launch-claude --no-continue "Start fresh"        # Start new conversation
    launch-claude -r "Resume with selection"          # Interactive resume
    launch-claude -r abc123 "Resume specific"         # Resume specific session
    launch-claude --quiet --no-logs "Simple query"   # Without logging
    launch-claude --log-file custom.log "Custom log" # Custom log file
    launch-claude --analyze-logs                      # Analyze logs
    launch-claude --clean-logs                        # Clean logs
    launch-claude --troubleshoot-mcp                  # Troubleshoot MCP

FEATURES:
    - Continue mode enabled by default - automatically resumes most recent conversation
    - All logging enabled by default for non-interactive mode (verbose, debug, MCP debug, save logs)
    - Interactive mode automatically disables verbose and logging for cleaner experience
    - Default model set to sonnet for optimal performance
    - Support for -c (continue) and -r (resume) flags with optional session ID
    - Automatic MCP configuration loading from centralized config
      (mcp-servers/mcp-config.json or legacy .mcp.json)
    - Automatic master prompt loading from $MASTER_PROMPT_FILE
    - Session-based logging to .acforge/logs/[SESSION]/ directory with timestamped folders
    - All log files include timestamps in their filenames (e.g. debug-20250802-085436.log)
    - MCP server debugging with telemetry support
    - Multi-agent log analysis using Claude Code agents
    - Auto-detection of devcontainer/codespace environments for permissions
    - Secure .env file loading with validation and masking of sensitive values

EOF
}

# Function to clean all log files
clean_logs() {
    echo "🧹 Cleaning all Claude Code session logs..."

    if [[ ! -d "$LOG_BASE_DIR" ]]; then
        echo "ℹ️  No log directory found at $LOG_BASE_DIR"
        return 0
    fi

    # Find all session directories (format: YYYYMMDD-HHMMSS)
    local session_dirs=($(find "$LOG_BASE_DIR" -maxdepth 1 -type d -name "[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9][0-9]" 2>/dev/null | sort))

    if [[ ${#session_dirs[@]} -eq 0 ]]; then
        echo "ℹ️  No session directories found to delete."
        return 0
    fi

    # Confirm destructive action
    echo "⚠️  This will permanently delete ALL session directories in:"
    echo "   📁 $LOG_BASE_DIR"
    echo

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

    read -p "Are you sure you want to delete ${#session_dirs[@]} session directories with $total_files files? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Log cleanup cancelled."
        return 1
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

    # Clean up empty base directory if needed
    if [[ -d "$LOG_BASE_DIR" ]] && [[ -z "$(ls -A "$LOG_BASE_DIR" 2>/dev/null)" ]]; then
        rmdir "$LOG_BASE_DIR" 2>/dev/null || true
    fi
}

# Function to troubleshoot MCP server issues using agents
troubleshoot_mcp() {
    echo "🔧 Troubleshooting MCP server issues using Claude Code agents..."

    # Check if log directory exists
    if [[ ! -d "$LOG_BASE_DIR" ]]; then
        echo "❌ No log directory found at $LOG_BASE_DIR"
        echo "💡 Run launch-claude with logging enabled first to generate logs for analysis."
        exit 1
    fi

    # Find relevant log files for MCP troubleshooting from recent sessions
    local session_dirs=($(find "$LOG_BASE_DIR" -maxdepth 1 -type d -name "[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9][0-9]" 2>/dev/null | sort -r | head -3))
    local session_logs=()
    local mcp_logs=()
    local debug_logs=()
    local telemetry_logs=()

    for session_dir in "${session_dirs[@]}"; do
        session_logs+=($(find "$session_dir" -name "session-*.log" -type f 2>/dev/null))
        mcp_logs+=($(find "$session_dir" -name "mcp-*.log" -type f 2>/dev/null))
        debug_logs+=($(find "$session_dir" -name "debug-*.log" -type f 2>/dev/null))
        telemetry_logs+=($(find "$session_dir" -name "telemetry-*.log" -type f 2>/dev/null))
    done

    # Also check for MCP configuration files
    local mcp_configs=()
    for mcp_config in "$PROJECT_ROOT/.mcp.json" "$PROJECT_ROOT/mcp-servers/mcp-config.json"; do
        if [[ -f "$mcp_config" ]]; then
            mcp_configs+=("$mcp_config")
        fi
    done

    # Combine all relevant files
    local all_files=("${session_logs[@]}" "${mcp_logs[@]}" "${debug_logs[@]}" "${telemetry_logs[@]}" "${mcp_configs[@]}")

    if [[ ${#all_files[@]} -eq 0 ]]; then
        echo "❌ No log files or MCP configuration files found for analysis."
        echo "💡 Run launch-claude with MCP features enabled first to generate data for troubleshooting."
        exit 1
    fi

    echo "🔍 Found files for MCP troubleshooting analysis:"
    echo "   📋 Session logs: ${#session_logs[@]}"
    echo "   🔌 MCP logs: ${#mcp_logs[@]}"
    echo "   🐛 Debug logs: ${#debug_logs[@]}"
    echo "   📊 Telemetry logs: ${#telemetry_logs[@]}"
    echo "   ⚙️  Configuration files: ${#mcp_configs[@]}"
    echo "   📁 Total files: ${#all_files[@]}"
    echo

    # Build analysis command with same permissions handling as main script
    local analysis_cmd=("claude" --model "$DEFAULT_MODEL")

    # Auto-detect environment for analysis command
    if [[ -n "${CODESPACES:-}" ]] || [[ -n "${REMOTE_CONTAINERS:-}" ]] || [[ -f "/.dockerenv" ]] || [[ -n "${DEVCONTAINER:-}" ]] || [[ "$SKIP_PERMISSIONS" == "true" ]]; then
        analysis_cmd+=(--dangerously-skip-permissions)
    fi

    # Use Claude Code with specialized agents for MCP troubleshooting
    echo "🤖 Launching specialized MCP troubleshooting analysis with multiple agents..."
    "${analysis_cmd[@]}" "Use the foundation-research, specialist-options-analyzer, foundation-patterns, and specialist-constraint-solver agents to perform comprehensive MCP server troubleshooting analysis on these files:

SESSION LOGS: ${session_logs[*]}
MCP SERVER LOGS: ${mcp_logs[*]}
DEBUG LOGS: ${debug_logs[*]}
TELEMETRY LOGS: ${telemetry_logs[*]}
CONFIGURATION FILES: ${mcp_configs[*]}

Please analyze and troubleshoot:

1. **MCP Server Connection Issues**:
   - Server startup and initialization problems
   - Connection establishment failures
   - Protocol handshake errors
   - Network connectivity issues

2. **Configuration Problems**:
   - Invalid or malformed MCP configuration
   - Missing required environment variables
   - Permission and access control issues
   - Path resolution problems

3. **Runtime Errors**:
   - Server crashes or unexpected exits
   - Memory leaks or resource exhaustion
   - Protocol violation errors
   - Communication timeouts

4. **Performance Issues**:
   - Slow response times
   - High resource usage
   - Request/response bottlenecks
   - Scalability concerns

5. **Integration Problems**:
   - Claude Code to MCP server communication
   - Tool execution failures
   - Data serialization/deserialization errors
   - State management issues

For each issue found, provide:
- Root cause analysis
- Step-by-step troubleshooting instructions
- Configuration fixes and recommendations
- Preventive measures for future issues
- Testing procedures to verify fixes

Focus on actionable solutions that can be implemented immediately to resolve MCP server problems."
}

# Function to analyze logs using Claude Code agents
analyze_logs() {
    echo "🔍 Analyzing logs using Claude Code agents..."

    # Check if log directory exists
    if [[ ! -d "$LOG_BASE_DIR" ]]; then
        echo "❌ No log directory found at $LOG_BASE_DIR"
        echo "💡 Run launch-claude with logging enabled first to generate logs."
        exit 1
    fi

    # Find recent session directories (last 5 sessions)
    local session_dirs=($(find "$LOG_BASE_DIR" -maxdepth 1 -type d -name "[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9][0-9]" 2>/dev/null | sort -r | head -5))

    if [[ ${#session_dirs[@]} -eq 0 ]]; then
        echo "❌ No session directories found in $LOG_BASE_DIR"
        echo "💡 Run launch-claude with logging enabled first to generate logs."
        exit 1
    fi

    # Collect log files from recent sessions
    local session_logs=()
    local mcp_logs=()
    local debug_logs=()
    local telemetry_logs=()

    for session_dir in "${session_dirs[@]}"; do
        # Find timestamped log files in each session directory
        local session_file=$(find "$session_dir" -name "session-*.log" -type f 2>/dev/null | head -1)
        local mcp_file=$(find "$session_dir" -name "mcp-*.log" -type f 2>/dev/null | head -1)
        local debug_file=$(find "$session_dir" -name "debug-*.log" -type f 2>/dev/null | head -1)
        local telemetry_file=$(find "$session_dir" -name "telemetry-*.log" -type f 2>/dev/null | head -1)

        if [[ -n "$session_file" ]]; then
            session_logs+=("$session_file")
        fi
        if [[ -n "$mcp_file" ]]; then
            mcp_logs+=("$mcp_file")
        fi
        if [[ -n "$debug_file" ]]; then
            debug_logs+=("$debug_file")
        fi
        if [[ -n "$telemetry_file" ]]; then
            telemetry_logs+=("$telemetry_file")
        fi
    done

    # Combine all log files
    local all_logs=("${session_logs[@]}" "${mcp_logs[@]}" "${debug_logs[@]}" "${telemetry_logs[@]}")

    if [[ ${#all_logs[@]} -eq 0 ]]; then
        echo "❌ No log files found in session directories"
        echo "💡 Run launch-claude with logging enabled first to generate logs."
        exit 1
    fi

    echo "📊 Found log files for analysis:"
    echo "   📅 Sessions analyzed: ${#session_dirs[@]}"
    echo "   📋 Session logs: ${#session_logs[@]}"
    echo "   🔌 MCP logs: ${#mcp_logs[@]}"
    echo "   🐛 Debug logs: ${#debug_logs[@]}"
    echo "   📊 Telemetry logs: ${#telemetry_logs[@]}"
    echo "   📁 Total files: ${#all_logs[@]}"
    echo

    # Build analysis command with same permissions handling as main script
    local analysis_cmd=("claude" --model "$DEFAULT_MODEL")

    # Auto-detect environment for analysis command (same logic as detect_environment)
    if [[ -n "${CODESPACES:-}" ]] || [[ -n "${REMOTE_CONTAINERS:-}" ]] || [[ -f "/.dockerenv" ]] || [[ -n "${DEVCONTAINER:-}" ]] || [[ "$SKIP_PERMISSIONS" == "true" ]]; then
        analysis_cmd+=(--dangerously-skip-permissions)
    fi

    # Use Claude Code with multiple agents for comprehensive analysis including security
    echo "🤖 Launching comprehensive log analysis with multiple agents..."
    "${analysis_cmd[@]}" "Use the researcher, patterns, vulnerability-scanner, and threat-modeling agents to analyze these log files comprehensively:

SESSION LOGS: ${session_logs[*]}
MCP LOGS: ${mcp_logs[*]}
DEBUG LOGS: ${debug_logs[*]}
TELEMETRY LOGS: ${telemetry_logs[*]}

Please analyze for:
1. Error patterns and failure modes
2. MCP server communication issues
3. Security vulnerabilities and threats
4. Attack patterns or suspicious activity
5. Data exposure risks in logs
6. Configuration security issues
7. Usage patterns and insights
8. Actionable recommendations for improvement

Focus on Claude Code usage patterns, not performance analysis of the launch-claude.sh script itself.
Provide a structured analysis with specific findings and actionable next steps."
}

# Parse command line arguments
ARGS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -q|--quiet)
            VERBOSE_MODE="false"
            shift
            ;;
        --no-debug)
            DEBUG_MODE="false"
            shift
            ;;
        --no-mcp-debug)
            MCP_DEBUG="false"
            shift
            ;;
        --no-logs)
            SAVE_LOGS="false"
            shift
            ;;
        --force-logs)
            SAVE_LOGS="force"
            shift
            ;;
        -m|--model)
            DEFAULT_MODEL="$2"
            shift 2
            ;;
        --log-file)
            LOG_FILE="$2"
            SAVE_LOGS="true"
            shift 2
            ;;
        --analyze-logs)
            analyze_logs
            exit 0
            ;;
        --clean-logs)
            clean_logs
            exit 0
            ;;
        --troubleshoot-mcp)
            troubleshoot_mcp
            exit 0
            ;;
        --skip-permissions)
            SKIP_PERMISSIONS="true"
            shift
            ;;
        --no-skip-permissions)
            SKIP_PERMISSIONS="false"
            shift
            ;;
        -c|--continue)
            USE_CONTINUE="true"
            USE_RESUME="false"
            shift
            ;;
        --no-continue)
            USE_CONTINUE="false"
            shift
            ;;
        -r|--resume)
            USE_CONTINUE="false"
            USE_RESUME="true"
            # Check if next argument exists and is not a flag
            if [[ -n "$2" && ! "$2" =~ ^- ]]; then
                RESUME_SESSION_ID="$2"
                shift 2
            else
                shift
            fi
            ;;
        --no-env)
            LOAD_ENV="false"
            shift
            ;;
        --env-file)
            if [[ -n "$2" ]]; then
                ENV_FILES=("$2")
                LOAD_ENV="true"
                shift 2
            else
                echo "❌ Error: --env-file requires a filename"
                exit 1
            fi
            ;;
        --dry-run)
            DRY_RUN="true"
            shift
            ;;
        *)
            ARGS+=("$1")
            shift
            ;;
    esac
done

# Setup session-based logging system
setup_logging() {
    # Convert "force" to "true" for consistency
    if [[ "$SAVE_LOGS" == "force" ]]; then
        SAVE_LOGS="true"
    fi
    
    if [[ "$SAVE_LOGS" == "true" ]]; then
        # Generate session timestamp
        SESSION_TIMESTAMP=$(date +"%Y%m%d-%H%M%S")

        # Create session directory with timestamp
        SESSION_DIR="$LOG_BASE_DIR/$SESSION_TIMESTAMP"
        mkdir -p "$SESSION_DIR"

        # Export session ID for MCP servers to use
        export CLAUDE_SESSION_ID="$SESSION_TIMESTAMP"

        # Set up log files in session directory with timestamps
        if [[ -z "$LOG_FILE" ]]; then
            LOG_FILE="$SESSION_DIR/launch-claude-session-$SESSION_TIMESTAMP.log"
        fi

        # Set up environment variables for comprehensive logging using official Claude Code standards
        export CLAUDE_CODE_ENABLE_TELEMETRY=1
        export CLAUDE_CODE_VERBOSE=1
        export MCP_TIMEOUT=30000

        # Configure OpenTelemetry for comprehensive telemetry collection
        export OTEL_LOGS_EXPORTER=console
        export OTEL_METRICS_EXPORTER=console
        export OTEL_TRACES_EXPORTER=console
        export OTEL_METRIC_EXPORT_INTERVAL=5000
        export OTEL_LOGS_EXPORT_INTERVAL=2000
        export OTEL_LOGS_LEVEL=DEBUG
        export OTEL_RESOURCE_ATTRIBUTES="service.name=launch-claude,service.version=1.0"

        # Create session-specific log files with timestamps
        local session_log="$SESSION_DIR/session-$SESSION_TIMESTAMP.log"
        local mcp_log="$SESSION_DIR/mcp-$SESSION_TIMESTAMP.log"
        local telemetry_log="$SESSION_DIR/telemetry-$SESSION_TIMESTAMP.log"
        local debug_log="$SESSION_DIR/debug-$SESSION_TIMESTAMP.log"
        local session_info="$SESSION_DIR/session-info-$SESSION_TIMESTAMP.txt"

        # Store paths for later use
        export MYCC_SESSION_LOG="$session_log"
        export MYCC_MCP_LOG="$mcp_log"
        export MYCC_TELEMETRY_LOG="$telemetry_log"
        export MYCC_DEBUG_LOG="$debug_log"
        export MYCC_SESSION_INFO="$session_info"

        # Create session info file
        cat > "$session_info" << EOF
Session: $SESSION_TIMESTAMP
Started: $(date)
Model: $DEFAULT_MODEL
Verbose: $VERBOSE_MODE
Debug: $DEBUG_MODE
MCP Debug: $MCP_DEBUG
Project: $PROJECT_ROOT
Claude Code Log Dir: $SESSION_DIR
Perplexity Log Dir: $PROJECT_ROOT/.acforge/logs/perplexity/$SESSION_TIMESTAMP
EOF

        echo "📝 Session-based logging enabled:"
        echo "   📁 Claude Code session directory: $SESSION_DIR"
        echo "   📁 Perplexity session directory: $PROJECT_ROOT/.acforge/logs/perplexity/$SESSION_TIMESTAMP"
        echo "   📋 Session log: $session_log"
        echo "   🔌 MCP log: $mcp_log"
        echo "   📊 Telemetry log: $telemetry_log"
        echo "   🐛 Debug log: $debug_log"
        echo "   ℹ️  Session info: $session_info"
        echo "   🆔 Session ID: $SESSION_TIMESTAMP (shared with MCP servers)"

        # Create empty log files to ensure they exist
        touch "$session_log" "$mcp_log" "$telemetry_log" "$debug_log"

        if [[ "$DEBUG_MODE" == "true" ]]; then
            echo "🔧 Log files created and ready for writing"
            echo "   Verbose mode: $VERBOSE_MODE"
            echo "   MCP debug: $MCP_DEBUG"
            echo "   Environment variables set for enhanced logging"
        fi
    fi
}

# Load master prompt if exists and has content
load_master_prompt() {
    MASTER_PROMPT_CONTENT=""

    if [[ -f "$MASTER_PROMPT_FILE" ]]; then
        local master_content
        master_content=$(cat "$MASTER_PROMPT_FILE")

        # Only use master prompt if it has non-whitespace content
        if [[ -n "${master_content// }" ]]; then
            echo "📋 Loading master prompt from $MASTER_PROMPT_FILE" >&2
            MASTER_PROMPT_CONTENT="$master_content"
        elif [[ "$DEBUG_MODE" == "true" ]]; then
            echo "ℹ️  Master prompt file exists but is empty, skipping" >&2
        fi
    elif [[ "$DEBUG_MODE" == "true" ]]; then
        echo "ℹ️  No master prompt file found at $MASTER_PROMPT_FILE" >&2
    fi
}

# Build Claude command with options
build_claude_command() {
    CLAUDE_CMD=("claude")

    # Set default model
    CLAUDE_CMD+=(--model "$DEFAULT_MODEL")

    # Add MCP configuration file - check multiple locations in priority order
    local mcp_config_found=""
    local mcp_config_locations=(
        "$PROJECT_ROOT/.mcp.json"                           # Project root (legacy)
        "$PROJECT_ROOT/mcp-servers/mcp-config.json"         # Centralized config
    )

    for mcp_config in "${mcp_config_locations[@]}"; do
        if [[ -f "$mcp_config" ]]; then
            mcp_config_found="$mcp_config"
            break
        fi
    done

    if [[ -n "$mcp_config_found" ]]; then
        CLAUDE_CMD+=(--mcp-config "$mcp_config_found")
        if [[ "$DEBUG_MODE" == "true" ]]; then
            echo "🔌 Using MCP config: $mcp_config_found" >&2
        fi
    elif [[ "$DEBUG_MODE" == "true" ]]; then
        echo "ℹ️  No MCP configuration file found" >&2
    fi

    # Add verbose mode if enabled
    if [[ "$VERBOSE_MODE" == "true" ]]; then
        CLAUDE_CMD+=(--verbose)
    fi

    # Add MCP debug if enabled
    if [[ "$MCP_DEBUG" == "true" ]]; then
        CLAUDE_CMD+=(--mcp-debug)
    fi

    # Add skip permissions if enabled (auto-detected or forced)
    if [[ "$SKIP_PERMISSIONS" == "true" ]]; then
        CLAUDE_CMD+=(--dangerously-skip-permissions)
    fi

    # Add continue or resume flags with conversation detection
    if [[ "$USE_CONTINUE" == "true" ]]; then
        if detect_conversations "$PROJECT_ROOT"; then
            CLAUDE_CMD+=(--continue)
            if [[ "$DEBUG_MODE" == "true" ]]; then
                echo "🔄 Continue mode: resuming existing conversation" >&2
            fi
        else
            if [[ "$DEBUG_MODE" == "true" ]]; then
                echo "🆕 No existing conversations found - starting new conversation" >&2
            fi
            # Don't add --continue flag when no conversations exist
        fi
    elif [[ "$USE_RESUME" == "true" ]]; then
        if [[ -n "$RESUME_SESSION_ID" ]]; then
            CLAUDE_CMD+=(--resume "$RESUME_SESSION_ID")
        else
            CLAUDE_CMD+=(--resume)
        fi
    fi

    # Add master prompt as system prompt only if it has meaningful content
    if [[ -n "$MASTER_PROMPT_CONTENT" ]]; then
        CLAUDE_CMD+=(--append-system-prompt)
        CLAUDE_CMD+=("$MASTER_PROMPT_CONTENT")
    fi

    # Debug environment variables are now set in setup_logging function
    # to use official Claude Code standards

    # Add user arguments
    CLAUDE_CMD+=("${ARGS[@]}")
}

# Main execution
main() {
    echo "🚀 launch-claude - Enhanced Claude Code wrapper"
    echo "📦 Model: $DEFAULT_MODEL"

    # Display session mode
    if [[ "$USE_CONTINUE" == "true" ]]; then
        echo "🔄 Continue mode: enabled (resuming most recent conversation)"
    elif [[ "$USE_RESUME" == "true" ]]; then
        if [[ -n "$RESUME_SESSION_ID" ]]; then
            echo "🔄 Resume mode: specific session ($RESUME_SESSION_ID)"
        else
            echo "🔄 Resume mode: interactive selection"
        fi
    else
        echo "🆕 New conversation mode"
    fi

    # For interactive mode, disable logging and verbose by default unless forced
    if [[ ${#ARGS[@]} -eq 0 ]] && [[ "$SAVE_LOGS" == "true" ]]; then
        # Disable logging in interactive mode to preserve stdin
        SAVE_LOGS="false"
        echo "ℹ️  Interactive mode: logging disabled (use --force-logs to enable)"
    elif [[ ${#ARGS[@]} -eq 0 ]] && [[ "$SAVE_LOGS" == "force" ]]; then
        SAVE_LOGS="true"
        echo "ℹ️  Interactive mode with forced logging enabled"
    fi

    # Disable verbose mode in interactive mode unless explicitly enabled
    if [[ ${#ARGS[@]} -eq 0 ]] && [[ "$VERBOSE_MODE" == "true" ]]; then
        VERBOSE_MODE="false"
        echo "ℹ️  Interactive mode: verbose disabled (use -q to explicitly disable or run with arguments to enable)"
    fi

    # Auto-detect environment before other setup
    detect_environment

    # Load configuration from .env files
    load_configuration

    setup_logging
    load_master_prompt

    build_claude_command

    if [[ "$DEBUG_MODE" == "true" ]] || [[ "$DRY_RUN" == "true" ]]; then
        echo "🔧 Debug mode enabled"
        echo "📝 Command: ${CLAUDE_CMD[*]}"
        echo
    fi

    # Exit early if dry run
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "🧪 Dry run complete - would execute: ${CLAUDE_CMD[*]}"
        exit 0
    fi

    # Execute Claude with comprehensive logging if requested
    if [[ "$SAVE_LOGS" == "true" ]]; then
        # Write session header to all relevant logs
        local session_header
        session_header="=== launch-claude session started at $(date) ===
Command: ${CLAUDE_CMD[*]}
Model: $DEFAULT_MODEL
Verbose: $VERBOSE_MODE
Debug: $DEBUG_MODE
MCP Debug: $MCP_DEBUG
Project: $PROJECT_ROOT
=========================="

        # Write headers to organized log files
        echo "$session_header" >> "$MYCC_SESSION_LOG"
        echo "$session_header" >> "$MYCC_DEBUG_LOG"

        # Execute Claude with comprehensive log redirection
        # Use reliable logging approach that captures all output streams
        {
            # Capture all output and separate by patterns
            "${CLAUDE_CMD[@]}" 2>&1 | while IFS= read -r line; do
                # Always output to terminal
                echo "$line"

                # Log to session and debug files
                echo "$line" >> "$MYCC_SESSION_LOG"
                echo "$line" >> "$MYCC_DEBUG_LOG"

                # Conditionally log to LOG_FILE if different from session log
                if [[ "$LOG_FILE" != "$MYCC_SESSION_LOG" ]]; then
                    echo "$line" >> "$LOG_FILE"
                fi

                # Detect and separate MCP output (case insensitive)
                if [[ "$line" =~ [Mm][Cc][Pp]|server|tool ]]; then
                    echo "$line" >> "$MYCC_MCP_LOG"
                fi

                # Detect and separate telemetry output (broader patterns)
                if [[ "$line" =~ [Tt]elemetry|[Tt]race|[Ss]pan|[Mm]etric|otel|OTEL ]]; then
                    echo "$line" >> "$MYCC_TELEMETRY_LOG"
                fi
            done
        }

        # Write session footer
        local session_footer="=== launch-claude session ended at $(date) ==="
        echo "$session_footer" >> "$MYCC_SESSION_LOG"
        echo "$session_footer" >> "$MYCC_DEBUG_LOG"
        echo "$session_footer" >> "$LOG_FILE"

    else
        # For interactive mode without logging, preserve terminal properly
        if [[ ${#ARGS[@]} -eq 0 ]]; then
            exec "${CLAUDE_CMD[@]}"
        else
            "${CLAUDE_CMD[@]}"
        fi
    fi
}

# Run main function
main