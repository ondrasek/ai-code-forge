#!/bin/bash

# Install development tools and dependencies
set -e

echo "📦 Installing development tools..."

# Install uv (modern Python package manager) - Secure installation via pip
echo "📦 Installing uv Python package manager..."
python3 -m pip install --user uv

# Install Claude CLI globally
echo "🤖 Installing Claude CLI, OpenAI Codex and OpenCode..."
npm install -g @anthropic-ai/claude-code
npm install -g @openai/codex
npm install -f opencode-ai

# Install MCP tools
echo "🔗 Installing MCP tools..."
npm install -g @modelcontextprotocol/inspector @modelcontextprotocol/server-sequential-thinking @modelcontextprotocol/server-memory

# Install Python development tools
echo "🛠️ Installing Python development tools..."
uv tool install ruff
uv tool install pytest
uv tool install mypy
uv tool install yamllint
uv tool install yq

echo "✅ Development tools installation completed"