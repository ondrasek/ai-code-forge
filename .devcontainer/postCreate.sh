#!/bin/bash

# DevContainer Setup Script - Replicates Codespace Environment
# This script sets up the exact same environment as the GitHub Codespace

# Install uv (modern Python package manager) - TODO; replace with pip install (this is insecure)
echo "📦 Installing uv Python package manager..."
curl -LsSf https://astral.sh/uv/install.sh | sh

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

# Skip the hassle when in GitHub Codespaces
if [ "$CODESPACES" = "true" ]; then
  echo "In Codespaces, exiting..."
  exit 0
fi

set -e

devcontainerDir=/tmp/.devcontainer 
eval "$(grep -v '^#' $devcontainerDir/postCreate.env.tmp | sed 's/^/export /')"
workingCopy=/workspace/$repositoryName

echo Configuration from initializeCommand:
echo repositoryName: $repositoryName
echo repositoryNameWithOwner: $repositoryNameWithOwner
echo gitUserName: $gitUserName
echo gitUserEmail: $gitUserEmail
echo workingCopt: $workingCopy

echo "🚀 Setting up Claude Code Template DevContainer..."
sudo mkdir -p /workspace && sudo chown vscode:vscode /workspace && cd /workspace

# Detect if we're in a container environment
export CONTAINER_ENV=1

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p ~/.claude

# Install and configure zsh
echo "🐚 Setting up zsh shell environment..."
sudo apt-get update && sudo apt-get install -y zsh

# Install Oh My Zsh for better zsh experience
if [ ! -d "$HOME/.oh-my-zsh" ]; then
    sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
fi

# Set zsh as default shell
sudo chsh -s $(which zsh) $USER

# Set up shell aliases and environment for both bash and zsh
echo "🐚 Configuring shell environment..."
cat >> ~/.bashrc << 'EOF'

# AI Code Forge Aliases
alias launch-claude='/workspace/ai-code-forge/scripts/launch-claude.sh'

# Environment variables for Claude Code
export PYTHONIOENCODING=UTF-8

# Add local bin to PATH
export PATH="$HOME/.local/bin:$PATH"
EOF

# ...thsi time with variable substitution
cat >> ~/.bashrc << EOF

# Go to workspace
cd /workspace/$repositoryName
EOF

# Configure zsh with same environment
cat >> ~/.zshrc << 'EOF'

# AI Code Forge Aliases
alias launch-claude='/workspace/ai-code-forge/scripts/launch-claude.sh'

# Environment variables for Claude Code
export PYTHONIOENCODING=UTF-8

# Add local bin to PATH
export PATH="$HOME/.local/bin:$PATH"

# Go to workspace
cd /workspace/$repositoryName
EOF

# ...this time with variable substitution
cat >> ~/.zshrc << EOF

# Go to workspace
cd /workspace/$repositoryName
EOF

# Set up Git configuration (if not already configured)
if [ -z "$(git config --global user.name)" ]; then
    echo "⚙️ Setting up basic Git configuration..."
    git config --global init.defaultBranch main
    git config --global pull.rebase false
    git config --global user.name $gitUserName
    git config --global user.email $gitUserEmail
fi

# Set up Git configuration and aliases
echo "🔧 Setting up Git configuration..."
echo 1. Credential Helper
git config --global credential.helper "!gh auth git-credential"
echo 2. Safe Directory: /workspace
git config --global --add safe.directory $workingCopy


# GitHub CLI authentication setup
echo "🔐 Setting up authentication..."
if gh auth status >/dev/null 2>&1; then
    echo "✅ GitHub CLI is already authenticated"
    gh auth status
else
    echo "⚠️  GitHub CLI not authenticated"
    echo "   Run 'gh auth login' after container setup completes"
    echo "   This will authenticate both GitHub CLI and git operations"
fi

echo "📋 Cloning repository into workspace:"
if [ -d $workingCopy/.git ]; then 
  cd $workingCopy
  gh repo sync
  cd -
else
  gh repo clone $repositoryNameWithOwner $workingCopy
fi

# Verify installations
echo "✅ Verifying installations..."
echo "Node.js: $(node --version)"
echo "npm: $(npm --version)"
echo "Python: $(python3 --version)"
echo "uv: $(uv --version)"
echo "Git: $(git --version)"
echo "gh: $(gh --version)"
echo "Claude CLI: $(claude --version 2>/dev/null || echo 'Claude CLI installed, requires API key for full verification')"

echo ""
echo "🎉 DevContainer setup completed successfully!"
echo ""
