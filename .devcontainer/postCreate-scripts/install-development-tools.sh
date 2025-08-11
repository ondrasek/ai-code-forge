#!/bin/bash

# Install development tools and dependencies
set -e

echo "📦 Installing development tools..."

# Install uv (modern Python package manager)
echo "🔄 Installing uv Python package manager..."
python3 -m pip install --user uv

# Install Claude CLI and AI tools
echo "🔄 Installing Claude CLI..."
npm install -g @anthropic-ai/claude-code

echo "🔄 Installing OpenAI Codex..."
npm install -g @openai/codex

echo "🔄 Installing OpenCode AI..."
npm install -g opencode-ai

# Install MCP tools
echo "🔄 Installing MCP Inspector..."
npm install -g @modelcontextprotocol/inspector
echo "🔄 Installing MCP Sequential Thinking..."
npm install -g @modelcontextprotocol/server-sequential-thinking 
echo "🔄 Installing MCP Memory..."
npm install -g @modelcontextprotocol/server-memory

# Install Python development tools
echo "🔄 Installing ruff..."
uv tool install ruff
echo "🔄 Installing pytest..."
uv tool install pytest
echo "🔄 Installing mypy..."
uv tool install mypy
echo "🔄 Installing yamllint..."
uv tool install yamllint
echo "🔄 Installing yq..."
uv tool install yq

echo "✅ Development tools installation completed"
