#!/bin/bash

# Install MCP (Model Context Protocol) tools
set -e

echo "🔗 Installing MCP tools..."

# Install MCP tools
echo "🔄 Installing MCP Inspector..."
npm install -g @modelcontextprotocol/inspector
echo "🔄 Installing MCP Sequential Thinking..."
npm install -g @modelcontextprotocol/server-sequential-thinking 
echo "🔄 Installing MCP Memory..."
npm install -g @modelcontextprotocol/server-memory

echo "✅ MCP tools installation completed"