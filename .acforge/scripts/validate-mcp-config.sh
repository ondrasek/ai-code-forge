#!/bin/bash
# Validate and test MCP server configurations

set -euo pipefail

echo "🔍 MCP Configuration Validator"
echo "============================="

# Function to validate JSON
validate_json() {
    local file="$1"
    if command -v jq >/dev/null 2>&1; then
        if jq empty < "$file" 2>/dev/null; then
            echo "  ✓ Valid JSON"
            return 0
        else
            echo "  ✗ Invalid JSON"
            return 1
        fi
    else
        echo "  ? JSON validation skipped (jq not available)"
        return 0
    fi
}

# Function to test MCP server
test_mcp_server() {
    local server_name="$1"
    echo "Testing server: $server_name"
    
    # Try to get server details
    if claude mcp get "$server_name" >/dev/null 2>&1; then
        echo "  ✓ Server configuration accessible"
    else
        echo "  ✗ Server configuration not accessible"
        return 1
    fi
    
    # Test server with a simple query
    echo "  Testing server with debug query..."
    if timeout 30s claude --debug --print "List available tools" 2>&1 | grep -q "$server_name"; then
        echo "  ✓ Server appears in debug output"
    else
        echo "  ? Server not found in debug output (may be normal)"
    fi
}

# Check configuration files
echo "📄 Configuration Files:"
for config_file in ".mcp.json" "mcp-servers/mcp-config.json"; do
    if [[ -f "$config_file" ]]; then
        echo "Found: $config_file"
        validate_json "$config_file"
        
        # Show server count if jq available
        if command -v jq >/dev/null 2>&1; then
            server_count=$(jq -r '.mcpServers | length' "$config_file" 2>/dev/null || echo "0")
            echo "  Servers defined: $server_count"
        fi
    fi
done

echo ""
echo "🔧 Configured Servers:"
# Test each configured server
claude mcp list | while read -r server_name; do
    if [[ -n "$server_name" && "$server_name" != "No MCP servers configured"* ]]; then
        test_mcp_server "$server_name"
        echo ""
    fi
done