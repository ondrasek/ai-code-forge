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

# Note: AI tools and MCP tools are installed in postCreate.sh after Node.js feature is available

# Configure shell PATH (oh-my-zsh handled by postCreate.sh)
RUN echo 'export PATH="$HOME/.local/bin:$PATH"' >> /home/vscode/.zshrc && \
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> /home/vscode/.bashrc

# Ensure vscode user owns all files in home directory
USER root
RUN chown -R vscode:vscode /home/vscode
USER vscode

# Set working directory back to workspace
WORKDIR /workspace