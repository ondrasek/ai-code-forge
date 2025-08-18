#!/bin/bash
# Analyze MCP server configuration and test connectivity

set -euo pipefail

echo "🔍 MCP Server Analysis"
echo "====================="

# List configured servers
echo "📋 Configured MCP Servers:"
claude mcp list

echo ""
echo "🔧 MCP Server Details:"
# Get details for each server (if any exist)
while read -r server_name; do
    if [[ -n "$server_name" && "$server_name" != "No MCP servers configured"* ]]; then
        echo "Server: $server_name"
        claude mcp get "$server_name" 2>/dev/null || echo "  Failed to get details"
        echo ""
    fi
done < <(claude mcp list 2>/dev/null | tail -n +2)

# Check for MCP configuration files
echo "📄 MCP Configuration Files:"
for config_file in ".mcp.json" "mcp-servers/mcp-config.json" ".claude/mcp-servers.json"; do
    if [[ -f "$config_file" ]]; then
        echo "  ✓ Found: $config_file"
        echo "    Size: $(wc -c < "$config_file") bytes"
        echo "    Modified: $(stat -c %y "$config_file" 2>/dev/null || stat -f %Sm "$config_file" 2>/dev/null)"
    else
        echo "  ✗ Not found: $config_file"
    fi
done

echo ""
echo "🌐 Environment Variables:"
env | grep -i claude | sort
echo ""
env | grep -i mcp | sort
echo ""
env | grep -i anthropic | sort