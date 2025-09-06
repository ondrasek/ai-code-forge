#!/bin/bash

# Install AI development tools
set -e

echo "🤖 Installing AI tools..."

# Install Claude CLI and AI tools
echo "🔄 Installing Claude CLI..."
npm install -g @anthropic-ai/claude-code

echo "🔄 Installing OpenAI Codex..."
npm install -g @openai/codex

echo "🔄 Installing OpenCode AI..."
npm install -g opencode-ai

echo "✅ AI tools installation completed"