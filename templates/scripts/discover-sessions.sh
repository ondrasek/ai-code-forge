#!/bin/bash
# Discover and analyze Claude Code JSONL session files

set -euo pipefail

CLAUDE_PROJECTS_DIR="$HOME/.claude/projects"

echo "🔍 Claude Code Session Discovery"
echo "==============================="

if [[ ! -d "$CLAUDE_PROJECTS_DIR" ]]; then
    echo "❌ Claude projects directory not found: $CLAUDE_PROJECTS_DIR"
    exit 1
fi

# Find all JSONL files
echo "📁 Scanning for JSONL files..."
JSONL_FILES=($(find "$CLAUDE_PROJECTS_DIR" -name "*.jsonl" -type f | sort))

if [[ ${#JSONL_FILES[@]} -eq 0 ]]; then
    echo "📭 No JSONL files found in $CLAUDE_PROJECTS_DIR"
    exit 0
fi

echo "📊 Found ${#JSONL_FILES[@]} JSONL session files"
echo ""

# Analyze each file
echo "📋 Session Summary:"
echo "==================="
printf "%-12s %-25s %-10s %-8s %-20s %-15s\n" "PROJECT" "SESSION" "MESSAGES" "SIZE" "LAST_MODIFIED" "BRANCH"
echo "$(printf '%*s' 90 '' | tr ' ' '-')"

for jsonl_file in "${JSONL_FILES[@]}"; do
    # Extract project and session info
    PROJECT=$(basename "$(dirname "$jsonl_file")" | cut -c1-20)
    SESSION=$(basename "$jsonl_file" .jsonl | cut -c1-8)
    
    # Get file stats
    MESSAGE_COUNT=$(wc -l < "$jsonl_file" 2>/dev/null || echo "0")
    FILE_SIZE=$(du -h "$jsonl_file" 2>/dev/null | cut -f1 || echo "0")
    LAST_MODIFIED=$(stat -c %y "$jsonl_file" 2>/dev/null | cut -d' ' -f1 || stat -f %Sm -t %Y-%m-%d "$jsonl_file" 2>/dev/null || echo "unknown")
    
    # Extract git branch from first line
    GIT_BRANCH=$(head -1 "$jsonl_file" 2>/dev/null | jq -r '.gitBranch // "unknown"' 2>/dev/null | cut -c1-15 || echo "unknown")
    
    printf "%-12s %-25s %-10s %-8s %-20s %-15s\n" \
        "$PROJECT" "$SESSION..." "$MESSAGE_COUNT" "$FILE_SIZE" "$LAST_MODIFIED" "$GIT_BRANCH"
done

echo ""
echo "🎯 Analysis Options:"
echo "==================="

# Find recent and large sessions
echo "📅 Recent Sessions (last 7 days):"
find "$CLAUDE_PROJECTS_DIR" -name "*.jsonl" -mtime -7 -exec basename {} \; | head -5 | while read session; do
    echo "  • $session"
done

echo ""
echo "📈 Largest Sessions (by message count):"
for jsonl_file in "${JSONL_FILES[@]}"; do
    MESSAGE_COUNT=$(wc -l < "$jsonl_file" 2>/dev/null || echo "0")
    echo "$MESSAGE_COUNT|$(basename "$jsonl_file")"
done | sort -nr | head -5 | while IFS='|' read count file; do
    echo "  • $file ($count messages)"
done

echo ""
echo "🔧 Tool Usage Analysis:"
echo "======================="

# Aggregate tool usage across all sessions
TEMP_TOOLS="/tmp/all_tools_$$"
TEMP_MCP_TOOLS="/tmp/mcp_tools_$$"
for jsonl_file in "${JSONL_FILES[@]}"; do
    jq -r 'select(.message.content[]?.type == "tool_use") | .message.content[]? | select(.type == "tool_use") | .name' "$jsonl_file" 2>/dev/null || true
done | sort | uniq -c | sort -nr > "$TEMP_TOOLS"

echo "Top 10 most used tools across all sessions:"
head -10 "$TEMP_TOOLS" | while read count tool; do
    echo "  • $tool: $count uses"
done

echo ""
echo "🔌 MCP Server Tool Detection:"
echo "============================"

# Known Claude Code built-in tools
BUILTIN_TOOLS="^(Bash|Read|Write|Edit|MultiEdit|Task|TodoWrite|LS|Grep|Glob|WebSearch|WebFetch|NotebookEdit)$"

# Find potential MCP tools (tools not in the built-in list)
grep -v -E "$BUILTIN_TOOLS" "$TEMP_TOOLS" > "$TEMP_MCP_TOOLS" 2>/dev/null || true

if [[ -s "$TEMP_MCP_TOOLS" ]]; then
    echo "Potential MCP server tools detected:"
    cat "$TEMP_MCP_TOOLS" | while read count tool; do
        echo "  • $tool: $count uses (potential MCP tool)"
    done
else
    echo "📭 No MCP server tools detected in JSONL files"
    echo "💡 This means either:"
    echo "  • No MCP servers were configured during these sessions"
    echo "  • MCP tools appear with different naming in JSONL files" 
    echo "  • MCP usage is captured differently than expected"
fi

echo ""
echo "🔍 MCP Server Configuration Analysis:"
echo "===================================="

# Check for MCP-related content in JSONL files
MCP_MENTIONS=0
for jsonl_file in "${JSONL_FILES[@]}"; do
    mentions=$(grep -i -c "mcp\|server.*add\|server.*config" "$jsonl_file" 2>/dev/null || echo "0")
    MCP_MENTIONS=$((MCP_MENTIONS + ${mentions:-0}))
done

if [[ $MCP_MENTIONS -gt 0 ]]; then
    echo "📊 Found $MCP_MENTIONS references to MCP/server configuration in JSONL files"
    echo "💡 Use './scripts/analyze-jsonl.sh <session.jsonl> mcp' for detailed MCP analysis"
else
    echo "📭 No MCP server configuration or usage detected"
    echo "💡 Sessions appear to use only built-in Claude Code tools"
fi

rm -f "$TEMP_TOOLS" "$TEMP_MCP_TOOLS"

echo ""
echo "💡 Quick Analysis Commands:"
echo "=========================="
echo ""

# Show most recent session for analysis
RECENT_SESSION=$(find "$CLAUDE_PROJECTS_DIR" -name "*.jsonl" -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2)
if [[ -n "$RECENT_SESSION" ]]; then
    echo "Analyze most recent session:"
    echo "  ./scripts/analyze-jsonl.sh \"$RECENT_SESSION\" summary"
    echo ""
fi

# Show largest session for analysis
LARGEST_SESSION=$(for f in "${JSONL_FILES[@]}"; do echo "$(wc -l < "$f")|$f"; done | sort -nr | head -1 | cut -d'|' -f2)
if [[ -n "$LARGEST_SESSION" ]]; then
    echo "Analyze largest session:"
    echo "  ./scripts/analyze-jsonl.sh \"$LARGEST_SESSION\" tools"
    echo ""
fi

echo "Analyze specific session:"
echo "  ./scripts/analyze-jsonl.sh <path-to-jsonl> <analysis-type>"
echo ""
echo "Analysis types: summary, tools, mcp, patterns, performance"
echo ""

echo "📊 Advanced Analysis:"
echo "===================="
echo ""
echo "Compare tool usage patterns:"
echo "  ./scripts/compare-sessions.sh session1.jsonl session2.jsonl"
echo ""
echo "Generate usage report:"
echo "  ./scripts/generate-usage-report.sh"
echo ""

# Offer interactive selection
echo "🎮 Interactive Analysis:"
echo "======================="
echo ""
read -p "Would you like to analyze a recent session? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] && [[ -n "$RECENT_SESSION" ]]; then
    echo "🚀 Analyzing most recent session..."
    exec ./scripts/analyze-jsonl.sh "$RECENT_SESSION" summary
fi