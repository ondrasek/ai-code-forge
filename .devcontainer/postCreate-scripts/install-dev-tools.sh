#!/bin/bash

# Install development tools and dependencies
set -e

echo "📦 Installing development tools..."

# Function to install tool with detailed logging
install_tool() {
    local tool_name="$1"
    local install_cmd="$2"
    local verify_cmd="$3"
    
    echo "🔄 Installing $tool_name..."
    if eval "$install_cmd" >/dev/null 2>&1; then
        if eval "$verify_cmd" >/dev/null 2>&1; then
            echo "✅ $tool_name: $(eval "$verify_cmd" 2>/dev/null)"
        else
            echo "⚠️  $tool_name: installed but verification failed"
        fi
    else
        echo "❌ $tool_name: installation failed"
        return 1
    fi
}

# Skip package installation in Codespaces (pre-installed)
if [ "$RUNTIME_ENV" = "codespaces" ]; then
    echo "🌐 Codespaces detected - verifying pre-installed tools..."
    
    # Verify tools are available
    command -v python3 >/dev/null || { echo "❌ Python3 missing"; exit 1; }
    command -v npm >/dev/null || { echo "❌ npm missing"; exit 1; }
    echo "✅ System tools verified"
else
    echo "🐳 DevContainer - installing all development tools..."
fi

# Install uv (modern Python package manager) - needed in all environments
install_tool "uv Python package manager" \
    "python3 -m pip install --user uv" \
    "uv --version"

# Install Claude CLI globally
install_tool "Claude CLI" \
    "npm install -g @anthropic-ai/claude-code" \
    "claude --version"

install_tool "OpenAI Codex" \
    "npm install -g @openai/codex" \
    "codex --version || echo 'codex installed'"

install_tool "OpenCode AI" \
    "npm install -g opencode-ai" \
    "opencode --version || echo 'opencode installed'"

# Install MCP tools
echo "🔗 Installing MCP tools..."
install_tool "MCP Inspector" \
    "npm install -g @modelcontextprotocol/inspector" \
    "npm list -g @modelcontextprotocol/inspector --depth=0"

install_tool "MCP Sequential Thinking" \
    "npm install -g @modelcontextprotocol/server-sequential-thinking" \
    "npm list -g @modelcontextprotocol/server-sequential-thinking --depth=0"

install_tool "MCP Memory" \
    "npm install -g @modelcontextprotocol/server-memory" \
    "npm list -g @modelcontextprotocol/server-memory --depth=0"

# Install Python development tools using uv
echo "🛠️ Installing Python development tools..."
install_tool "ruff" "uv tool install ruff" "ruff --version"
install_tool "pytest" "uv tool install pytest" "pytest --version"
install_tool "mypy" "uv tool install mypy" "mypy --version"
install_tool "yamllint" "uv tool install yamllint" "yamllint --version"
install_tool "yq" "uv tool install yq" "yq --version"

echo "✅ Development tools installation completed"
