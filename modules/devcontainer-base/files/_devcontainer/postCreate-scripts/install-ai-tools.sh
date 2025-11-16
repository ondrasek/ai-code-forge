#!/bin/bash

# Install AI development tools
set -e

echo "🤖 Installing AI tools..."

# Install Claude CLI and AI tools
echo "🔄 Installing Claude CLI..."
npm install -g @anthropic-ai/claude-code

# OpenAI Codex and OpenCode AI support removed in v4.0.0

echo "✅ AI tools installation completed"