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

# Switch to vscode user for tool installations  
USER vscode
WORKDIR /home/vscode

# Verify vscode user and install Python tools with cache optimization
RUN --mount=type=cache,target=/home/vscode/.cache/pip,uid=1000,gid=1000 \
    echo "vscode user UID: $(id -u), GID: $(id -g)" && \
    python3 -m pip install --user uv && \
    /home/vscode/.local/bin/uv --version

# Add ~/.local/bin to PATH for subsequent RUN commands
ENV PATH="/home/vscode/.local/bin:${PATH}"

# Install uv tools with cache optimization
RUN --mount=type=cache,target=/home/vscode/.cache/uv,uid=1000,gid=1000 \
    uv tool install ruff && \
    uv tool install pytest && \
    uv tool install mypy && \
    uv tool install yamllint && \
    uv tool install yq

# Install AI tools with cache optimization
RUN --mount=type=cache,target=/home/vscode/.npm,uid=1000,gid=1000 \
    npm install -g @anthropic-ai/claude-code && \
    npm install -g @openai/codex && \
    npm install -g opencode-ai

# Install MCP tools with cache optimization
RUN --mount=type=cache,target=/home/vscode/.npm,uid=1000,gid=1000 \
    npm install -g @modelcontextprotocol/inspector && \
    npm install -g @modelcontextprotocol/server-sequential-thinking && \
    npm install -g @modelcontextprotocol/server-memory

# Configure oh-my-zsh
RUN git clone https://github.com/ohmyzsh/ohmyzsh.git /home/vscode/.oh-my-zsh && \
    cp /home/vscode/.oh-my-zsh/templates/zshrc.zsh-template /home/vscode/.zshrc && \
    echo 'export ZSH="$HOME/.oh-my-zsh"' >> /home/vscode/.zshrc && \
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> /home/vscode/.zshrc && \
    echo 'source $ZSH/oh-my-zsh.sh' >> /home/vscode/.zshrc

# Also configure bash for completeness
RUN echo 'export PATH="$HOME/.local/bin:$PATH"' >> /home/vscode/.bashrc

# Ensure vscode user owns all files in home directory
USER root
RUN chown -R vscode:vscode /home/vscode
USER vscode

# Set working directory back to workspace
WORKDIR /workspace