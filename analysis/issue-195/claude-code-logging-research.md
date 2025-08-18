# Claude Code Logging Capabilities Research

## RESEARCH FINDINGS: Built-in Logging Support

### ✅ Confirmed: Automatic JSONL Transcripts

**Claude Code DOES have built-in persistent logging** - but not in the traditional log file format:

#### 1. Automatic Session Transcripts
- **Location**: `~/.claude/projects/[project-hash]/[session-id].jsonl`
- **Format**: JSONL (JSON Lines) with complete conversation history
- **Content**: Full tool usage, MCP calls, user input, assistant responses
- **Retention**: Configurable via `cleanupPeriodDays` setting (default: 30 days)

#### 2. Transcript Content Structure
```json
{
  "parentUuid": "...",
  "sessionId": "64d9845f-4824-401d-a436-0abae773e8c4",
  "version": "1.0.83",
  "gitBranch": "issue-191-fix-launch-claude-sh",
  "type": "user|assistant",
  "message": {
    "role": "user|assistant",
    "content": "...",
    "tool_use": [...],
    "usage": {...}
  },
  "timestamp": "2025-08-18T07:40:18.649Z"
}
```

#### 3. What's Captured in JSONL Transcripts
- ✅ Complete user input and assistant responses
- ✅ All tool executions (Bash, Read, Write, etc.)
- ✅ Tool parameters and results
- ✅ Session metadata (git branch, working directory)
- ✅ Timestamps for all interactions
- ✅ Usage statistics (tokens, etc.)

### ❌ Missing: Traditional Log Files

**Claude Code does NOT provide:**
- No `--log-file` flag or equivalent
- No structured debug log files
- No MCP-specific log files
- No system logging integration (syslog/journald)
- No real-time log streaming

### 🔧 Available Debug Output Mechanisms

#### Console Output Only
```bash
# Debug output to stdout/stderr (what we've been capturing)
claude --debug --verbose                    # Debug info to console
export ANTHROPIC_LOG=debug                  # Additional debug output
claude --output-format stream-json          # Structured output format
```

#### Configuration-Based Logging
- `cleanupPeriodDays`: Controls JSONL transcript retention
- No other logging configuration options found

## PRACTICAL IMPLICATIONS FOR OUR USE CASES

### ✅ What We CAN Extract from JSONL Transcripts

#### 1. MCP Server Usage Analysis
JSONL transcripts contain complete tool execution records:
```json
{
  "type": "assistant",
  "message": {
    "content": [
      {
        "type": "tool_use",
        "id": "toolu_01GVe6UtLbGFjigfNF6Vf9ZB",
        "name": "Bash",
        "input": {
          "command": "gh issue view 191",
          "description": "Get issue details"
        }
      }
    ]
  }
}
```

#### 2. Tool Usage Pattern Analysis  
- Complete tool invocation history with parameters
- Success/failure status (if available in responses)
- Timing information via timestamps
- Working directory and git branch context

#### 3. Sub-Agent Context (Limited)
- Can infer agent context from conversation flow
- Tool usage patterns may indicate specific agent behaviors
- Session metadata provides execution context

### ❌ What We CANNOT Get from JSONL Transcripts

#### 1. Real-Time MCP Server Communication
- No direct MCP protocol message capture
- No MCP server startup/connection logs
- No MCP server performance metrics

#### 2. Sub-Agent Internal Operations
- No visibility into Task() delegation mechanisms
- No agent-to-agent communication logs
- No internal agent decision processes

#### 3. System-Level Debug Information
- No file system operations details
- No network request specifics
- No performance profiling data

## IMPLEMENTATION RECOMMENDATIONS

### High Priority: JSONL Transcript Analysis

#### 1. Build JSONL Parser for Analytics
```bash
# Location of transcripts
ls ~/.claude/projects/*/

# Parse for tool usage
jq '.message.content[]? | select(.type == "tool_use")' session.jsonl

# Extract MCP-related activity  
jq '.message.content[]? | select(.name | test("mcp|server|github"))' session.jsonl
```

#### 2. Create Transcript Analysis Scripts
- **`analyze-transcripts.sh`**: Parse JSONL for tool/MCP usage
- **`extract-tool-patterns.sh`**: Analyze tool usage patterns
- **`session-analytics.sh`**: Generate analytics from multiple sessions

#### 3. Supplement with Console Capture
- Continue using our console capture scripts for real-time debugging
- Combine with JSONL analysis for comprehensive view
- Use console capture for MCP debug output not in transcripts

### Medium Priority: Third-Party Tool Integration

#### Community Tools Found
- `claude-code-log`: Third-party logging enhancement
- `claude-notes`: Session note-taking and analysis
- Various user-created transcript parsers

#### Integration Approach
- Evaluate existing community tools for JSONL processing
- Build custom analytics on top of Claude's native transcripts
- Consider contributing improvements back to community

### Low Priority: Feature Requests

#### Missing Capabilities to Request
- Official `--log-file` flag for structured logging
- MCP server debug log output
- Real-time log streaming API
- System logging integration

## CONCLUSION

**Claude Code DOES have persistent logging** via automatic JSONL transcripts that contain comprehensive session data including tool usage, which directly addresses your use cases.

**Our Implementation Strategy Should:**
1. **Primary**: Build analytics on top of existing JSONL transcripts
2. **Secondary**: Continue console capture for real-time debugging
3. **Supplementary**: Evaluate community tools for enhanced processing

This is actually **better than traditional log files** for your analytics needs because:
- Complete conversation context preserved
- Structured JSON format easy to parse
- Automatic retention management
- No additional configuration required

The JSONL transcripts provide the foundation for comprehensive analytics about MCP usage, tool patterns, and session behavior - exactly what you need for your four scenarios.