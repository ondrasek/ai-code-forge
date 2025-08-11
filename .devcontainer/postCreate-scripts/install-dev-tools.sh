#!/bin/bash

# Install development tools and dependencies
set -e

echo "📦 Installing development tools..."

# Skip some installations in Codespaces (pre-installed)
if [ "$RUNTIME_ENV" = "codespaces" ]; then
    echo "🌐 Codespaces detected - skipping system packages"
else
    echo "🐳 DevContainer - installing all development tools"
fi

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
echo "🔄 Installing MCP tools..."
npm install -g @modelcontextprotocol/inspector
npm install -g @modelcontextprotocol/server-sequential-thinking 
npm install -g @modelcontextprotocol/server-memory

# Install Python development tools
echo "🔄 Installing Python development tools..."
uv tool install ruff
uv tool install pytest
uv tool install mypy
uv tool install yamllint
uv tool install yq

echo "✅ Development tools installation completed"
