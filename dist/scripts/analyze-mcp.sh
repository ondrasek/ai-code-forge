#!/bin/bash
# Analyze MCP server configuration and test connectivity

set -euo pipefail

echo "🔍 MCP Server Analysis"
echo "====================="
echo "ℹ️  Analyzing actual Claude Code MCP configuration and debug output"
echo ""

# Create temp log for analysis
TEMP_LOG="/tmp/mcp-analysis-$(date +%s).log"

# List configured servers
echo "📋 Configured MCP Servers:"
claude mcp list | tee "$TEMP_LOG"

echo ""
echo "🔧 MCP Server Details:"
# Get details for each server (if any exist)
server_count=0
while read -r server_name; do
    if [[ -n "$server_name" && "$server_name" != "No MCP servers configured"* && "$server_name" != "Configured MCP Servers:" ]]; then
        echo "Server: $server_name"
        if claude mcp get "$server_name" 2>/dev/null; then
            ((server_count++))
        else
            echo "  ⚠️  Failed to get server details"
        fi
        echo ""
    fi
done < <(claude mcp list 2>/dev/null)

if [[ $server_count -eq 0 ]]; then
    echo "📭 No MCP servers currently configured"
    echo "💡 Add a server with: claude mcp add <name> <command>"
fi

# Check for MCP configuration files
echo "📄 MCP Configuration Files:"
config_found=false
for config_file in ".mcp.json" "mcp-servers/mcp-config.json" ".claude/mcp-servers.json"; do
    if [[ -f "$config_file" ]]; then
        echo "  ✓ Found: $config_file"
        echo "    Size: $(wc -c < "$config_file") bytes"
        echo "    Modified: $(stat -c %y "$config_file" 2>/dev/null || stat -f %Sm "$config_file" 2>/dev/null)"
        config_found=true
        
        # Show server count if jq available
        if command -v jq >/dev/null 2>&1; then
            if server_count=$(jq -r '.mcpServers | length' "$config_file" 2>/dev/null); then
                echo "    Servers defined: $server_count"
            fi
        fi
    else
        echo "  ✗ Not found: $config_file"
    fi
done

if [[ "$config_found" == "false" ]]; then
    echo "📭 No MCP configuration files found"
    echo "💡 Create .mcp.json or use 'claude mcp add' to configure servers"
fi

echo ""
echo "🌐 Relevant Environment Variables:"
echo "Claude Code variables:"
env | grep -i claude | sort || echo "  (none found)"
echo ""
echo "MCP variables:"
env | grep -i mcp | sort || echo "  (none found)" 
echo ""
echo "Anthropic variables:"
env | grep -i anthropic | sort || echo "  (none found)"

echo ""
echo "🔍 Test Debug Output (checking for MCP activity):"
echo "Running: claude --debug --print 'test' to see debug output..."
if timeout 10s claude --debug --print "test debug output" 2>&1 | head -5; then
    echo "✓ Debug output available"
else
    echo "⚠️  Debug command timed out or failed"
fi

# Cleanup
rm -f "$TEMP_LOG"

echo ""
echo "💡 Next steps:"
echo "  • Add MCP server: claude mcp add <name> <command>"
echo "  • Test with debug: ./debug-claude.sh \"your query\""
echo "  • Validate config: ./validate-mcp-config.sh"