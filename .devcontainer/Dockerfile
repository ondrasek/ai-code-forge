# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/devcontainers/python:latest

# Install system updates and packages with cache optimization
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y zsh curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python tools with cache optimization
RUN --mount=type=cache,target=/root/.cache/pip \
    python3 -m pip install --user uv

# Switch to vscode user for tool installations
USER vscode
WORKDIR /home/vscode

# Install uv tools with user context and cache optimization
RUN --mount=type=cache,target=/home/vscode/.cache/uv \
    /home/vscode/.local/bin/uv tool install ruff && \
    /home/vscode/.local/bin/uv tool install pytest && \
    /home/vscode/.local/bin/uv tool install mypy && \
    /home/vscode/.local/bin/uv tool install yamllint && \
    /home/vscode/.local/bin/uv tool install yq

# Install AI tools with cache optimization
RUN --mount=type=cache,target=/home/vscode/.npm \
    npm install -g @anthropic-ai/claude-code && \
    npm install -g @openai/codex && \
    npm install -g opencode-ai

# Install MCP tools with cache optimization
RUN --mount=type=cache,target=/home/vscode/.npm \
    npm install -g @modelcontextprotocol/inspector && \
    npm install -g @modelcontextprotocol/server-sequential-thinking && \
    npm install -g @modelcontextprotocol/server-memory

# Configure oh-my-zsh
RUN git clone https://github.com/ohmyzsh/ohmyzsh.git /home/vscode/.oh-my-zsh && \
    cp /home/vscode/.oh-my-zsh/templates/zshrc.zsh-template /home/vscode/.zshrc && \
    echo 'export ZSH="$HOME/.oh-my-zsh"' >> /home/vscode/.zshrc && \
    echo 'source $ZSH/oh-my-zsh.sh' >> /home/vscode/.zshrc

# Ensure vscode user owns all files in home directory
USER root
USER vscode
RUN chown -R vscode:vscode /home/vscode

# Set working directory back to workspace
WORKDIR /workspace