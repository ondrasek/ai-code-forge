#!/bin/bash
# Analyze Claude Code JSONL files using Claude Code itself

set -euo pipefail

JSONL_PATH="$1"
ANALYSIS_TYPE="${2:-summary}"

if [[ ! -f "$JSONL_PATH" ]]; then
    echo "❌ JSONL file not found: $JSONL_PATH"
    echo "Usage: $0 <jsonl-file> [analysis-type]"
    echo ""
    echo "Analysis types:"
    echo "  summary     - General session summary"
    echo "  tools       - Tool usage analysis"
    echo "  mcp         - MCP server usage analysis"
    echo "  patterns    - Workflow patterns"
    echo "  performance - Performance analysis"
    exit 1
fi

echo "🔍 Analyzing JSONL file: $(basename "$JSONL_PATH")"
echo "📊 Analysis type: $ANALYSIS_TYPE"
echo ""

# Quick file stats
FILE_SIZE=$(du -h "$JSONL_PATH" | cut -f1)
LINE_COUNT=$(wc -l < "$JSONL_PATH")
echo "📄 File size: $FILE_SIZE"
echo "📝 Total messages: $LINE_COUNT"
echo ""

# Create temporary analysis directory
TEMP_DIR="/tmp/claude-jsonl-analysis-$$"
mkdir -p "$TEMP_DIR"

# Generate basic statistics
STATS_FILE="$TEMP_DIR/stats.txt"
{
    echo "=== JSONL File Analysis Stats ==="
    echo "File: $JSONL_PATH"
    echo "Size: $FILE_SIZE"
    echo "Messages: $LINE_COUNT"
    echo ""
    
    echo "=== Tool Usage Count ==="
    jq -r 'select(.message.content[]?.type == "tool_use") | .message.content[]? | select(.type == "tool_use") | .name' "$JSONL_PATH" | sort | uniq -c | sort -nr || echo "No tool usage found"
    echo ""
    
    echo "=== Message Types ==="
    jq -r '.type' "$JSONL_PATH" | sort | uniq -c || echo "No message types found"
    echo ""
    
    echo "=== Session Information ==="
    head -1 "$JSONL_PATH" | jq -r '"Session ID: " + .sessionId, "Git Branch: " + .gitBranch, "Working Dir: " + .cwd, "Claude Version: " + .version'
    echo ""
    
    echo "=== Conversation Timeline ==="
    echo "First message: $(head -1 "$JSONL_PATH" | jq -r '.timestamp')"
    echo "Last message: $(tail -1 "$JSONL_PATH" | jq -r '.timestamp')"
    
} > "$STATS_FILE"

# Display basic stats
cat "$STATS_FILE"

# Create analysis prompt based on type
case "$ANALYSIS_TYPE" in
    "summary")
        PROMPT="Analyze this Claude Code session JSONL data and provide a comprehensive summary including:

1. **Session Overview**: What was this session about? What tasks were accomplished?
2. **Tool Usage Patterns**: Which tools were used most frequently and why?
3. **Workflow Analysis**: What was the overall workflow and methodology?
4. **Key Accomplishments**: What concrete outputs or decisions were made?
5. **Technical Insights**: Any interesting technical patterns or approaches?

Focus on understanding the user's goals and how Claude Code was used to achieve them."
        ;;
        
    "tools")
        PROMPT="Analyze the tool usage patterns in this Claude Code session. Provide insights on:

1. **Tool Frequency Analysis**: Which tools were used most/least and why?
2. **Tool Combinations**: What sequences or patterns of tool usage occurred?
3. **Task-Tool Correlation**: How do different tools correlate with different types of tasks?
4. **Efficiency Analysis**: Were tools used effectively? Any redundant usage?
5. **Missing Tools**: What tasks might have benefited from different tools?

Extract specific examples from the JSONL data to support your analysis."
        ;;
        
    "mcp")
        PROMPT="Analyze MCP server and external service usage in this Claude Code session:

1. **MCP Server Detection**: Identify any MCP server usage or configuration
2. **External Service Calls**: Look for GitHub CLI, API calls, or external integrations  
3. **Service Patterns**: How were external services integrated into the workflow?
4. **Configuration Analysis**: Any MCP or service configuration activities?
5. **Integration Effectiveness**: How well did external services support the tasks?

Focus on understanding the interaction between Claude Code and external systems."
        ;;
        
    "patterns")
        PROMPT="Analyze workflow and behavioral patterns in this Claude Code session:

1. **Work Methodology**: What approach did the user/AI take to accomplish tasks?
2. **Decision Making**: How were technical decisions made and documented?
3. **Research Patterns**: How was information gathering and analysis conducted?
4. **Agent Usage**: Were there patterns of using Task() for specialized agents?
5. **Problem Solving**: What problem-solving approaches were effective?

Identify reusable patterns and methodologies that could inform future sessions."
        ;;
        
    "performance")
        PROMPT="Analyze performance and efficiency aspects of this Claude Code session:

1. **Session Duration**: How long did the session take? (check timestamps)
2. **Tool Efficiency**: Were tools used efficiently? Any bottlenecks?
3. **Workflow Optimization**: Could the workflow have been more efficient?
4. **Resource Usage**: Analysis of computational resources and API calls
5. **Productivity Metrics**: Tasks accomplished vs time/resources invested

Provide recommendations for improving future session efficiency."
        ;;
        
    *)
        echo "❌ Unknown analysis type: $ANALYSIS_TYPE"
        rm -rf "$TEMP_DIR"
        exit 1
        ;;
esac

# Use Claude Code to analyze the JSONL file
echo "🤖 Generating AI analysis..."
echo ""

ANALYSIS_PROMPT="$PROMPT

Here are the basic statistics:
$(cat "$STATS_FILE")

Please analyze the attached JSONL file with this context. The JSONL file contains a complete Claude Code conversation session with all tool usage, messages, and metadata."

# Run Claude Code analysis
claude --print "$ANALYSIS_PROMPT

Please read and analyze the JSONL file: $JSONL_PATH" 2>/dev/null || {
    echo "⚠️  Direct JSONL analysis failed. Trying with extracted data..."
    
    # Extract recent tool usage for analysis
    echo "Recent tool executions:" > "$TEMP_DIR/recent_tools.txt"
    jq -r 'select(.message.content[]?.type == "tool_use") | .timestamp + " | " + (.message.content[]? | select(.type == "tool_use") | .name + ": " + (.input.description // .input.command // .input.file_path // "no description"))' "$JSONL_PATH" | tail -20 >> "$TEMP_DIR/recent_tools.txt"
    
    claude --print "$ANALYSIS_PROMPT

Based on the statistics above and these recent tool executions:
$(cat "$TEMP_DIR/recent_tools.txt")

Please provide your analysis."
}

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "✅ Analysis complete!"
echo ""
echo "💡 Usage examples:"
echo "  $0 ~/.claude/projects/*/session.jsonl summary"
echo "  $0 ~/.claude/projects/*/session.jsonl tools"
echo "  $0 ~/.claude/projects/*/session.jsonl mcp"