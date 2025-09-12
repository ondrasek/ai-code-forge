#!/bin/bash

# launch-codex - Enhanced OpenAI Codex CLI wrapper with custom configuration  
# Usage: launch-codex [options] [query]
#
# This script provides a custom wrapper around codex with:
# - Enhanced defaults with logging enabled
# - ChatGPT subscription authentication support
# - Custom configuration loading from ~/.codex/config.toml
# - Enhanced verbose logging capabilities
# - Session-based logging to .acforge/logs/codex/
# - Auto-detection of devcontainer/codespace environments

set -euo pipefail

# Source shared utilities
SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/lib"

if [[ ! -f "$LIB_DIR/launcher-utils.sh" ]]; then
    echo "❌ Error: Required library not found: $LIB_DIR/launcher-utils.sh"
    exit 1
fi

source "$LIB_DIR/launcher-utils.sh"

# Initialize paths using shared utility
init_paths "$SCRIPT_PATH"

# Configuration variables
DEFAULT_MODEL="gpt-4"
VERBOSE_MODE="true"
DEBUG_MODE="true"
LOG_FILE=""
SAVE_LOGS="true"
SKIP_PERMISSIONS="false"
USE_CONTINUE="true"
USE_RESUME="false"
RESUME_SESSION_ID=""
DRY_RUN="false"
AUTH_MODE="chatgpt"  # "chatgpt" or "api-key"

# Environment file configuration
ENV_FILES=(".env" ".env.local" ".env.development")
LOAD_ENV="true"

# Codex-specific configuration
CODEX_CONFIG_FILE="$HOME/.codex/config.toml"
CODEX_PROFILE="default"
APPROVAL_MODE="suggest"  # "suggest", "auto-edit", "full-auto"

# Help function
show_help() {
    cat << EOF
launch-codex - Enhanced OpenAI Codex CLI wrapper

USAGE:
    launch-codex [OPTIONS] [QUERY]

OPTIONS:
    -h, --help                Show this help message
    -q, --quiet              Disable verbose mode (overrides default enable)
    --no-debug               Disable debug mode (overrides default enable)
    --no-logs                Disable log saving (overrides default enable)
    --force-logs             Force enable logging even in interactive mode
    -m, --model MODEL        Set model (default: $DEFAULT_MODEL)
    --log-file FILE          Save logs to specified file (default: timestamped)
    -c, --continue           Continue the most recent conversation (default: enabled)
    --no-continue            Disable continue mode (start new conversation)
    -r, --resume [ID]        Resume a conversation (with optional session ID)
    --dry-run                Show what would be executed without running
    --analyze-logs           Analyze existing log files using Claude Code agents
    --clean-logs             Remove all existing session directories from .acforge/logs/codex/
    --troubleshoot-codex     Analyze and troubleshoot Codex CLI issues using agents
    --skip-permissions       Force enable --dangerously-skip-permissions flag
    --no-skip-permissions    Force disable --dangerously-skip-permissions flag
    --no-env                 Disable .env file loading
    --env-file FILE          Load specific .env file (can be used multiple times)
    --auth-mode MODE         Authentication mode: "chatgpt" or "api-key" (default: $AUTH_MODE)
    --profile PROFILE        Codex configuration profile (default: $CODEX_PROFILE)
    --approval-mode MODE     Approval mode: "suggest", "auto-edit", "full-auto" (default: $APPROVAL_MODE)

CODEX-SPECIFIC OPTIONS:
    --config FILE            Use specific Codex config file (default: ~/.codex/config.toml)
    --suggest                Use suggest approval mode (review changes before applying)
    --auto-edit              Use auto-edit mode (apply changes with confirmation)
    --full-auto              Use full-auto mode (apply changes without confirmation)

EXAMPLES:
    launch-codex "Review my code"                      # Continue most recent conversation
    launch-codex --no-continue "Start fresh"          # Start new conversation
    launch-codex -r "Resume with selection"           # Interactive resume
    launch-codex -r abc123 "Resume specific"          # Resume specific session
    launch-codex --quiet --no-logs "Simple query"     # Without logging
    launch-codex --log-file custom.log "Custom log"   # Custom log file
    launch-codex --analyze-logs                       # Analyze logs
    launch-codex --clean-logs                         # Clean logs
    launch-codex --troubleshoot-codex                 # Troubleshoot Codex
    launch-codex --auth-mode api-key "API mode"       # Use API key authentication
    launch-codex --auto-edit "Implement feature"      # Auto-edit approval mode
    launch-codex --profile work "Work context"        # Use work profile

FEATURES:
    - Continue mode enabled by default - automatically resumes most recent conversation
    - All logging enabled by default for non-interactive mode (verbose, debug, save logs)
    - Interactive mode automatically disables verbose and logging for cleaner experience
    - Default model set to gpt-4 for optimal performance
    - Support for -c (continue) and -r (resume) flags with optional session ID
    - ChatGPT subscription authentication with fallback to API key
    - Automatic Codex configuration loading from ~/.codex/config.toml
    - Session-based logging to .acforge/logs/codex/[SESSION]/ directory with timestamped folders
    - All log files include timestamps in their filenames (e.g. debug-20250812-123456.log)
    - Codex CLI debugging with Rust logging support (RUST_LOG)
    - Multi-agent log analysis using Claude Code agents
    - Auto-detection of devcontainer/codespace environments for permissions
    - Secure .env file loading with validation and masking of sensitive values
    - Multiple approval modes for different workflows and safety requirements

EOF
}

# Function to analyze logs using Claude Code agents
analyze_logs() {
    echo "🔍 Analyzing Codex logs using Claude Code agents..."

    # Check if log directory exists
    local log_base_dir="$PROJECT_ROOT/.acforge/logs/codex"
    if [[ ! -d "$log_base_dir" ]]; then
        echo "❌ No log directory found at $log_base_dir"
        echo "💡 Run launch-codex with logging enabled first to generate logs."
        exit 1
    fi

    # Find recent session directories using shared utility
    local session_dirs=($(find_recent_sessions "codex" "$PROJECT_ROOT" 5))

    if [[ ${#session_dirs[@]} -eq 0 ]]; then
        echo "❌ No session directories found in $log_base_dir"
        echo "💡 Run launch-codex with logging enabled first to generate logs."
        exit 1
    fi

    # Collect log files from recent sessions
    local session_logs=()
    local codex_logs=()
    local debug_logs=()
    local telemetry_logs=()

    for session_dir in "${session_dirs[@]}"; do
        # Find timestamped log files in each session directory
        local session_file=$(find "$session_dir" -name "session-*.log" -type f 2>/dev/null | head -1)
        local codex_file=$(find "$session_dir" -name "codex-*.log" -type f 2>/dev/null | head -1)
        local debug_file=$(find "$session_dir" -name "debug-*.log" -type f 2>/dev/null | head -1)
        local telemetry_file=$(find "$session_dir" -name "telemetry-*.log" -type f 2>/dev/null | head -1)

        if [[ -n "$session_file" ]]; then
            session_logs+=("$session_file")
        fi
        if [[ -n "$codex_file" ]]; then
            codex_logs+=("$codex_file")
        fi
        if [[ -n "$debug_file" ]]; then
            debug_logs+=("$debug_file")
        fi
        if [[ -n "$telemetry_file" ]]; then
            telemetry_logs+=("$telemetry_file")
        fi
    done

    # Combine all log files
    local all_logs=("${session_logs[@]}" "${codex_logs[@]}" "${debug_logs[@]}" "${telemetry_logs[@]}")

    if [[ ${#all_logs[@]} -eq 0 ]]; then
        echo "❌ No log files found in session directories"
        echo "💡 Run launch-codex with logging enabled first to generate logs."
        exit 1
    fi

    echo "📊 Found log files for analysis:"
    echo "   📅 Sessions analyzed: ${#session_dirs[@]}"
    echo "   📋 Session logs: ${#session_logs[@]}"
    echo "   🔧 Codex logs: ${#codex_logs[@]}"
    echo "   🐛 Debug logs: ${#debug_logs[@]}"
    echo "   📊 Telemetry logs: ${#telemetry_logs[@]}"
    echo "   📁 Total files: ${#all_logs[@]}"
    echo

    # Build analysis command with same permissions handling as main script
    local analysis_cmd=("claude" --model "sonnet")

    # Auto-detect environment for analysis command
    detect_environment
    if [[ "$DETECTED_SKIP_PERMISSIONS" == "true" ]] || [[ "$SKIP_PERMISSIONS" == "true" ]]; then
        analysis_cmd+=(--dangerously-skip-permissions)
    fi

    # Use Claude Code with multiple agents for comprehensive analysis
    echo "🤖 Launching comprehensive Codex log analysis with multiple agents..."
    "${analysis_cmd[@]}" "Use the researcher, patterns, and constraint-solver agents to analyze these Codex CLI log files comprehensively:

SESSION LOGS: ${session_logs[*]}
CODEX LOGS: ${codex_logs[*]}
DEBUG LOGS: ${debug_logs[*]}
TELEMETRY LOGS: ${telemetry_logs[*]}

Please analyze for:
1. Error patterns and failure modes specific to Codex CLI
2. Authentication and authorization issues
3. Configuration problems with ~/.codex/config.toml
4. Performance bottlenecks and resource usage
5. Usage patterns and workflow insights
6. Security considerations and potential vulnerabilities
7. Integration issues with project environments
8. Actionable recommendations for improvement

Focus on Codex CLI usage patterns, configuration optimization, and workflow improvements.
Provide a structured analysis with specific findings and actionable next steps."
}

# Function to troubleshoot Codex CLI issues using agents
troubleshoot_codex() {
    echo "🔧 Troubleshooting Codex CLI issues using Claude Code agents..."

    # Check if log directory exists
    local log_base_dir="$PROJECT_ROOT/.acforge/logs/codex"
    if [[ ! -d "$log_base_dir" ]]; then
        echo "❌ No log directory found at $log_base_dir"
        echo "💡 Run launch-codex with logging enabled first to generate logs for analysis."
        exit 1
    fi

    # Find relevant log files for troubleshooting from recent sessions
    local session_dirs=($(find_recent_sessions "codex" "$PROJECT_ROOT" 3))
    local session_logs=()
    local codex_logs=()
    local debug_logs=()
    local telemetry_logs=()

    for session_dir in "${session_dirs[@]}"; do
        session_logs+=($(find "$session_dir" -name "session-*.log" -type f 2>/dev/null))
        codex_logs+=($(find "$session_dir" -name "codex-*.log" -type f 2>/dev/null))
        debug_logs+=($(find "$session_dir" -name "debug-*.log" -type f 2>/dev/null))
        telemetry_logs+=($(find "$session_dir" -name "telemetry-*.log" -type f 2>/dev/null))
    done

    # Also check for Codex configuration files
    local config_files=()
    if [[ -f "$CODEX_CONFIG_FILE" ]]; then
        config_files+=("$CODEX_CONFIG_FILE")
    fi
    if [[ -f "$HOME/.codex/profiles.toml" ]]; then
        config_files+=("$HOME/.codex/profiles.toml")
    fi

    # Combine all relevant files
    local all_files=("${session_logs[@]}" "${codex_logs[@]}" "${debug_logs[@]}" "${telemetry_logs[@]}" "${config_files[@]}")

    if [[ ${#all_files[@]} -eq 0 ]]; then
        echo "❌ No log files or Codex configuration files found for analysis."
        echo "💡 Run launch-codex with logging enabled first to generate data for troubleshooting."
        exit 1
    fi

    echo "🔍 Found files for Codex troubleshooting analysis:"
    echo "   📋 Session logs: ${#session_logs[@]}"
    echo "   🔧 Codex logs: ${#codex_logs[@]}"
    echo "   🐛 Debug logs: ${#debug_logs[@]}"
    echo "   📊 Telemetry logs: ${#telemetry_logs[@]}"
    echo "   ⚙️  Configuration files: ${#config_files[@]}"
    echo "   📁 Total files: ${#all_files[@]}"
    echo

    # Build analysis command with same permissions handling as main script
    local analysis_cmd=("claude" --model "sonnet")

    # Auto-detect environment for analysis command
    detect_environment
    if [[ "$DETECTED_SKIP_PERMISSIONS" == "true" ]] || [[ "$SKIP_PERMISSIONS" == "true" ]]; then
        analysis_cmd+=(--dangerously-skip-permissions)
    fi

    # Use Claude Code with specialized agents for Codex troubleshooting
    echo "🤖 Launching specialized Codex troubleshooting analysis with multiple agents..."
    "${analysis_cmd[@]}" "Use the researcher, options-analyzer, patterns, and constraint-solver agents to perform comprehensive Codex CLI troubleshooting analysis on these files:

SESSION LOGS: ${session_logs[*]}
CODEX LOGS: ${codex_logs[*]}
DEBUG LOGS: ${debug_logs[*]}
TELEMETRY LOGS: ${telemetry_logs[*]}
CONFIGURATION FILES: ${config_files[*]}

Please analyze and troubleshoot:

1. **Authentication Issues**:
   - ChatGPT subscription authentication failures
   - API key configuration problems
   - Token expiration and refresh issues
   - Permission and access control problems

2. **Configuration Problems**:
   - Invalid or malformed TOML configuration
   - Profile selection and switching issues
   - Model availability and selection problems
   - Environment variable conflicts

3. **Runtime Errors**:
   - Codex CLI crashes or unexpected exits
   - Memory issues or resource exhaustion
   - Network connectivity problems
   - File system permission errors

4. **Performance Issues**:
   - Slow response times
   - High resource usage
   - Network timeout problems
   - Rate limiting issues

5. **Integration Problems**:
   - Environment detection failures
   - Project context loading issues
   - File encoding or path problems
   - Shell integration conflicts

For each issue found, provide:
- Root cause analysis
- Step-by-step troubleshooting instructions
- Configuration fixes and recommendations
- Preventive measures for future issues
- Testing procedures to verify fixes

Focus on actionable solutions that can be implemented immediately to resolve Codex CLI problems."
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
            clean_tool_logs "codex" "$PROJECT_ROOT"
            exit 0
            ;;
        --troubleshoot-codex)
            troubleshoot_codex
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
        --auth-mode)
            if [[ "$2" =~ ^(chatgpt|api-key)$ ]]; then
                AUTH_MODE="$2"
                shift 2
            else
                echo "❌ Error: --auth-mode must be 'chatgpt' or 'api-key'"
                exit 1
            fi
            ;;
        --profile)
            CODEX_PROFILE="$2"
            shift 2
            ;;
        --approval-mode)
            if [[ "$2" =~ ^(suggest|auto-edit|full-auto)$ ]]; then
                APPROVAL_MODE="$2"
                shift 2
            else
                echo "❌ Error: --approval-mode must be 'suggest', 'auto-edit', or 'full-auto'"
                exit 1
            fi
            ;;
        --config)
            CODEX_CONFIG_FILE="$2"
            shift 2
            ;;
        --suggest)
            APPROVAL_MODE="suggest"
            shift
            ;;
        --auto-edit)
            APPROVAL_MODE="auto-edit"
            shift
            ;;
        --full-auto)
            APPROVAL_MODE="full-auto"
            shift
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

# Build Codex command with options
build_codex_command() {
    CODEX_CMD=("npx" "@openai/codex")

    # Set model
    CODEX_CMD+=(--model "$DEFAULT_MODEL")

    # Set authentication mode
    case "$AUTH_MODE" in
        chatgpt)
            CODEX_CMD+=(--auth chatgpt)
            ;;
        api-key)
            CODEX_CMD+=(--auth api-key)
            ;;
    esac

    # Set approval mode
    case "$APPROVAL_MODE" in
        suggest)
            CODEX_CMD+=(--approve suggest)
            ;;
        auto-edit)
            CODEX_CMD+=(--approve auto-edit)
            ;;
        full-auto)
            CODEX_CMD+=(--approve full-auto)
            ;;
    esac

    # Add configuration file if it exists
    if [[ -f "$CODEX_CONFIG_FILE" ]]; then
        CODEX_CMD+=(--config "$CODEX_CONFIG_FILE")
        if [[ "$DEBUG_MODE" == "true" ]]; then
            echo "⚙️  Using Codex config: $CODEX_CONFIG_FILE" >&2
        fi
    elif [[ "$DEBUG_MODE" == "true" ]]; then
        echo "ℹ️  No Codex configuration file found at $CODEX_CONFIG_FILE" >&2
    fi

    # Add profile if not default
    if [[ "$CODEX_PROFILE" != "default" ]]; then
        CODEX_CMD+=(--profile "$CODEX_PROFILE")
    fi

    # Add verbose mode if enabled
    if [[ "$VERBOSE_MODE" == "true" ]]; then
        CODEX_CMD+=(--verbose)
    fi

    # Add quiet mode if verbose is disabled
    if [[ "$VERBOSE_MODE" == "false" ]]; then
        CODEX_CMD+=(--quiet)
    fi

    # Add user arguments
    CODEX_CMD+=("${ARGS[@]}")
}

# Main execution
main() {
    echo "🚀 launch-codex - Enhanced OpenAI Codex CLI wrapper"
    echo "📦 Model: $DEFAULT_MODEL"
    echo "🔐 Auth mode: $AUTH_MODE"
    echo "📋 Approval mode: $APPROVAL_MODE"

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

    # Validate tool requirements
    if ! validate_tool_requirements "Codex CLI" "npx"; then
        echo "💡 Install Node.js and npm to use npx with Codex"
        echo "💡 Codex will be run via: npx @openai/codex"
        exit 1
    fi

    # Auto-detect environment
    # Check for devcontainer environment or CI environment
    if [[ -n "${CODESPACES:-}" ]] || [[ -n "${REMOTE_CONTAINERS:-}" ]] || [[ -f "/.dockerenv" ]] || [[ -n "${DEVCONTAINER:-}" ]] || [[ -n "${GITHUB_ACTIONS:-}" ]] || [[ -n "${CI:-}" ]]; then
        echo "🔍 Detected devcontainer/codespace environment - enabling --dangerously-skip-permissions"
        SKIP_PERMISSIONS="true"
    fi

    # Load configuration from .env files
    if [[ "$LOAD_ENV" == "true" ]]; then
        load_configuration "$PROJECT_ROOT" "$DEBUG_MODE" "${ENV_FILES[@]}"
    fi

    # Convert "force" to "true" for consistency
    if [[ "$SAVE_LOGS" == "force" ]]; then
        SAVE_LOGS="true"
    fi
    
    # Setup session-based logging
    if [[ "$SAVE_LOGS" == "true" ]]; then
        setup_session_logging "codex" "$PROJECT_ROOT" "$DEBUG_MODE" "$SAVE_LOGS"
    fi

    build_codex_command

    if [[ "$DEBUG_MODE" == "true" ]] || [[ "$DRY_RUN" == "true" ]]; then
        echo "🔧 Debug mode enabled"
        echo "📝 Command: ${CODEX_CMD[*]}"
        echo
    fi

    # Exit early if dry run
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "🧪 Dry run complete - would execute: ${CODEX_CMD[*]}"
        exit 0
    fi

    # Execute Codex with comprehensive logging if requested
    if [[ "$SAVE_LOGS" == "true" ]]; then
        execute_with_logging "${CODEX_CMD[@]}"
    else
        # For interactive mode without logging, preserve terminal properly
        if [[ ${#ARGS[@]} -eq 0 ]]; then
            exec "${CODEX_CMD[@]}"
        else
            "${CODEX_CMD[@]}"
        fi
    fi
}

# Run main function
main