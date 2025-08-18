SITUATIONAL CONTEXT ANALYSIS
============================

SITUATION UNDERSTANDING:
User needs to understand how Claude Code stores conversations and how to properly detect if a conversation exists before using the -c (--continue) argument, as mentioned in issue #191. This is critical for fixing the launch-claude.sh script's conversation handling.

RELEVANT CODEBASE CONTEXT:
- Key Components: Claude Code stores conversations in ~/.claude/projects/[project-name]/ as JSONL files
- Related Patterns: Both launch-claude.sh and launch-codex.sh support -c/--continue and -r/--resume flags
- Dependencies: Claude Code CLI, filesystem access to ~/.claude/ directory
- Constraints: Must handle cases where no conversation exists gracefully

HISTORICAL CONTEXT:
- Past Decisions: The script currently defaults to USE_CONTINUE="true" but doesn't validate conversation existence
- Evolution: Issue #191 identified that -c argument handling needs conversation detection to avoid errors
- Lessons Learned: From research-findings.md - need to use official Claude Code environment variables
- Success Patterns: The launcher-utils.sh library provides session detection functions for logs

SITUATIONAL RECOMMENDATIONS:
- Suggested Approach: Implement conversation detection based on Claude Code's storage patterns before using -c flag
- Key Considerations: Handle multiple project directories, detect most recent conversation, graceful fallback
- Implementation Notes: Use ~/.claude/projects/ structure and JSONL file detection
- Testing Strategy: Test with existing conversations, no conversations, and corrupted conversation files

IMPACT ANALYSIS:
- Affected Systems: launch-claude.sh script, conversation continuity workflows
- Risk Assessment: Low risk - only improves robustness, no breaking changes
- Documentation Needs: Update help text and implementation comments
- Migration Requirements: None - backward compatible enhancement

## Technical Implementation Analysis

### Claude Code Conversation Storage Structure

**Location**: `~/.claude/projects/`

**Directory Structure**:
```
~/.claude/projects/
├─ -workspace-ai-code-forge/
│  ├─ 0fa01f13-52ab-46af-bea9-0b26dd233778.jsonl
│  ├─ 16866ec3-a6dc-4ba6-adb7-7fb92d38af18.jsonl
│  └─ ... (more conversation files)
├─ -workspace-worktrees-ai-code-forge-issue-191/
│  └─ 64d9845f-4824-401d-a436-0abae773e8c4.jsonl
└─ ... (other project directories)
```

**Key Findings**:
1. Project directories are named based on workspace path with slashes replaced by dashes
2. Each conversation is stored as a separate `.jsonl` file with UUID naming
3. Files contain conversation history in JSON Lines format
4. Most recent conversation can be determined by file modification time

### Current launch-claude.sh Conversation Handling

**Current Implementation Issues**:
1. **Default Continue Mode**: Script defaults to `USE_CONTINUE="true"` without validation
2. **No Conversation Detection**: Script passes `--continue` to Claude Code without checking if conversations exist
3. **Error Handling**: If no conversation exists, Claude Code may fail or start new conversation unexpectedly
4. **Inconsistent Behavior**: User experience varies based on conversation history state

**Current Code Pattern** (lines 752-761):
```bash
# Add continue or resume flags
if [[ "$USE_CONTINUE" == "true" ]]; then
    CLAUDE_CMD+=(--continue)
elif [[ "$USE_RESUME" == "true" ]]; then
    if [[ -n "$RESUME_SESSION_ID" ]]; then
        CLAUDE_CMD+=(--resume "$RESUME_SESSION_ID")
    else
        CLAUDE_CMD+=(--resume)
    fi
fi
```

### MCP Configuration Path Analysis

**Current Issue**: Script documentation mentions `.support/mcp-servers/mcp-config.json` but actual path is `mcp-servers/mcp-config.json`

**Current Implementation** (lines 714-735):
```bash
local mcp_config_locations=(
    "$PROJECT_ROOT/.mcp.json"                           # Project root (legacy)
    "$PROJECT_ROOT/mcp-servers/mcp-config.json"         # Centralized config
)
```

**Analysis**: The implementation is correct - help text is outdated and should be updated.

### Conversation Detection Implementation Strategy

**Recommended Function**:
```bash
# Detect if conversations exist for current project
detect_conversations() {
    local project_path="$1"
    local conversation_count=0
    local most_recent_conversation=""
    
    # Generate project directory name (replace / with -)
    local project_name
    project_name=$(echo "$project_path" | sed 's|/|-|g' | sed 's|^-||')
    
    local claude_projects_dir="$HOME/.claude/projects/$project_name"
    
    if [[ -d "$claude_projects_dir" ]]; then
        # Find .jsonl conversation files
        local conversation_files=($(find "$claude_projects_dir" -name "*.jsonl" -type f 2>/dev/null))
        conversation_count=${#conversation_files[@]}
        
        if [[ $conversation_count -gt 0 ]]; then
            # Find most recent conversation by modification time
            most_recent_conversation=$(ls -t "${conversation_files[@]}" 2>/dev/null | head -1)
        fi
    fi
    
    # Return results via global variables
    export DETECTED_CONVERSATION_COUNT="$conversation_count"
    export DETECTED_MOST_RECENT_CONVERSATION="$most_recent_conversation"
    
    return $([[ $conversation_count -gt 0 ]] && echo 0 || echo 1)
}
```

**Integration Points**:
1. Call `detect_conversations` before building Claude command
2. Only add `--continue` flag if conversations exist
3. Provide user feedback about conversation status
4. Gracefully fall back to new conversation mode if no conversations found

### Environment Variables Update Requirements

**From research-findings.md Analysis**:

**Current Deprecated Variables** (to remove):
- `ANTHROPIC_DEBUG=1` → Not officially supported
- `ANTHROPIC_LOG_LEVEL=debug` → Not officially supported  
- `CLAUDE_DEBUG=1` → Not officially supported
- `MCP_LOG_LEVEL=debug` → Not officially supported

**Official Claude Code Variables** (to add):
- `CLAUDE_CODE_ENABLE_TELEMETRY=1` → Enable OpenTelemetry export
- `CLAUDE_CODE_VERBOSE` → Show full bash and command outputs  
- `OTEL_LOGS_EXPORTER=console` → Local logging
- `OTEL_METRIC_EXPORT_INTERVAL` → Metrics export interval
- `OTEL_LOGS_EXPORT_INTERVAL` → Logs export interval

### Implementation Priority

**High Priority**: Conversation Detection
1. Implement `detect_conversations()` function
2. Integrate conversation detection before `--continue` flag usage
3. Update user feedback to show conversation status
4. Test with various conversation states

**High Priority**: Environment Variables Migration  
1. Replace deprecated variables with official Claude Code variables
2. Update telemetry configuration using OTEL_* variables
3. Use `--verbose` CLI flag instead of ANTHROPIC_DEBUG
4. Validate against official Claude Code documentation

**Medium Priority**: Documentation Updates
1. Fix MCP configuration path references in help text
2. Update example usage to reflect conversation detection
3. Document new environment variables

**Low Priority**: Testing and Validation
1. Add unit tests for conversation detection
2. Test edge cases (corrupted conversations, permission issues)
3. Validate with different Claude Code versions

### Edge Cases and Error Handling

**Conversation Detection Edge Cases**:
1. **No ~/.claude Directory**: Handle gracefully, fall back to new conversation
2. **Permission Issues**: Handle access denied to ~/.claude/projects/
3. **Corrupted JSONL Files**: Detect and skip corrupted conversation files  
4. **Project Name Mapping**: Handle complex workspace paths correctly
5. **Multiple Conversations**: Always use most recent by modification time

**Error Handling Strategy**:
```bash
# Safe conversation detection with error handling
detect_conversations_safe() {
    local project_path="$1"
    
    # Set defaults
    export DETECTED_CONVERSATION_COUNT="0"
    export DETECTED_MOST_RECENT_CONVERSATION=""
    
    # Handle missing .claude directory
    if [[ ! -d "$HOME/.claude" ]]; then
        if [[ "$DEBUG_MODE" == "true" ]]; then
            echo "ℹ️  No ~/.claude directory found - will start new conversation"
        fi
        return 1
    fi
    
    # Handle permission issues
    if [[ ! -r "$HOME/.claude/projects" ]]; then
        if [[ "$DEBUG_MODE" == "true" ]]; then
            echo "⚠️  Cannot read ~/.claude/projects - permission issue"
        fi
        return 1
    fi
    
    # Continue with normal detection...
    detect_conversations "$project_path"
}
```

### Testing Strategy

**Unit Tests** (for launcher-units.sh):
1. Test conversation detection with existing conversations
2. Test conversation detection with no conversations  
3. Test conversation detection with permission issues
4. Test project name mapping for various workspace paths
5. Test error handling for corrupted directories

**Integration Tests**:
1. Test full launch-claude.sh with conversation detection
2. Test environment variable migration
3. Test MCP configuration loading
4. Test logging functionality with new variables

**Manual Testing Scenarios**:
1. Fresh workspace with no conversations → should start new conversation
2. Workspace with existing conversations → should use --continue
3. Workspace with corrupted conversation files → should handle gracefully
4. Permission restricted ~/.claude directory → should fall back safely

### Security Considerations

**File System Access**:
- Only read from ~/.claude/projects/ directory
- No modification of conversation files
- Handle permission denied gracefully
- Validate file paths to prevent directory traversal

**Environment Variables**:
- Validate environment variable values
- Mask sensitive API keys in debug output
- Use official Claude Code variables only

## Analysis Documentation

### Context Sources:
- `/workspace/worktrees/ai-code-forge/issue-191/scripts/launch-claude.sh` - Current implementation
- `/workspace/worktrees/ai-code-forge/issue-191/scripts/lib/launcher-utils.sh` - Shared utilities
- `/workspace/worktrees/ai-code-forge/issue-191/analysis/issue-191/research-findings.md` - Environment variable research
- `~/.claude/projects/` - Claude Code conversation storage structure
- Claude Code CLI help output - Official flag documentation

### Key Discoveries:
- Claude Code stores conversations as JSONL files in `~/.claude/projects/[project-name]/`
- Project names are workspace paths with slashes replaced by dashes
- Most recent conversation can be detected by file modification time
- Current script uses deprecated environment variables that need migration
- MCP configuration path in help text is incorrect but implementation is correct

### Decision Factors:
- Must maintain backward compatibility with existing usage patterns
- Need to handle edge cases gracefully without breaking existing workflows
- Should provide clear user feedback about conversation status
- Must use official Claude Code environment variables for reliable functionality
- Should implement robust error handling for file system access issues