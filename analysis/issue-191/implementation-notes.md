# Implementation Notes - Issue #191 Fix

## Priority Implementation Plan

Based on comprehensive research and context analysis, here's the implementation roadmap for fixing the launch-claude.sh script:

## High Priority Fixes

### 1. Environment Variables Migration
**Current Issues**: Using deprecated/non-standard environment variables
**Fix**: Replace with official Claude Code 2025 standards

**Remove These (lines 623-628)**:
```bash
export CLAUDE_DEBUG=1
export ANTHROPIC_DEBUG=1
export ANTHROPIC_LOG_LEVEL=debug
export MCP_DEBUG=1
export MCP_LOG_LEVEL=debug
```

**Replace With**:
```bash
export CLAUDE_CODE_ENABLE_TELEMETRY=1
export CLAUDE_CODE_VERBOSE=1
export OTEL_LOGS_EXPORTER=console
export OTEL_METRIC_EXPORT_INTERVAL=5000
export OTEL_LOGS_EXPORT_INTERVAL=2000
```

### 2. Conversation Detection Implementation
**Current Issue**: `-c` flag used blindly without checking if conversations exist
**Fix**: Add conversation detection before using `--continue`

**Implementation Location**: `build_claude_command()` function (lines 752-761)

**New Function Needed**:
```bash
detect_conversations() {
    local project_path="$1"
    local project_name=$(echo "$project_path" | sed 's|/|-|g' | sed 's|^-||')
    local claude_projects_dir="$HOME/.claude/projects/$project_name"
    
    if [[ -d "$claude_projects_dir" ]]; then
        local conversation_files=($(find "$claude_projects_dir" -name "*.jsonl" -type f 2>/dev/null))
        if [[ ${#conversation_files[@]} -gt 0 ]]; then
            return 0  # Conversations found
        fi
    fi
    return 1  # No conversations found
}
```

### 3. Help Text Correction
**Current Issue**: Help text mentions incorrect MCP config path
**Fix**: Update line 212 help text to match actual implementation

**Change**:
```
FROM: (.support/mcp-servers/mcp-config.json or legacy .mcp.json)
TO:   (mcp-servers/mcp-config.json or legacy .mcp.json)
```

## Implementation Details

### Environment Variables Changes

**File**: `scripts/launch-claude.sh`

**Lines 622-629 (setup_logging function)**:
Replace deprecated environment variable setup with official Claude Code standards.

**Lines 770-774 (build_claude_command function)**:
Remove duplicate debug environment variable setting, rely on setup_logging configuration.

### Conversation Detection Integration

**File**: `scripts/launch-claude.sh`

**New function to add after line 49 (detect_environment function)**:
Add `detect_conversations()` function for conversation existence checking.

**Lines 752-761 modification**:
Replace simple `--continue` flag addition with conversation detection logic:
```bash
if [[ "$USE_CONTINUE" == "true" ]]; then
    if detect_conversations "$PROJECT_ROOT"; then
        CLAUDE_CMD+=(--continue)
        if [[ "$DEBUG_MODE" == "true" ]]; then
            echo "🔄 Continue mode: conversations detected" >&2
        fi
    else
        if [[ "$DEBUG_MODE" == "true" ]]; then
            echo "🆕 No conversations found - starting new conversation" >&2
        fi
        # Don't add --continue flag
    fi
fi
```

### CLI Project Location Discrepancy

**Files**: 
- `scripts/launch-claude.sh` (main implementation)
- `cli/src/ai_code_forge/data/acf/scripts/launch-claude.sh` (CLI data copy)

**Action**: Both files are identical copies. Need to fix both or establish which is canonical.

## Testing Strategy

### Manual Testing Scenarios
1. **Fresh workspace**: No conversations exist - should start new conversation
2. **Existing conversations**: Conversations exist - should continue latest
3. **Permission issues**: ~/.claude directory not accessible - should fail gracefully
4. **Environment variables**: All logging should use official Claude Code variables

### Validation Steps
1. Verify no deprecated environment variables are set
2. Confirm conversation detection works with various project names
3. Test MCP configuration path resolution
4. Validate help text accuracy

## Risk Assessment

### Low Risk Changes
- Help text correction
- Environment variable names (backwards compatible)

### Medium Risk Changes
- Conversation detection logic (new behavior)
- CLI flag conditional logic (could affect existing workflows)

### Dependencies
- Claude Code CLI must be installed and accessible
- ~/.claude directory structure must be consistent with current Claude Code versions
- Project naming conventions must match Claude Code's internal logic

## Success Criteria

- [ ] Environment variables use official Claude Code standards
- [ ] -c argument only used when conversations exist
- [ ] Logging provides useful debug output using official mechanisms
- [ ] Help text reflects actual implementation
- [ ] Script maintains backwards compatibility for basic usage