#!/bin/bash

# Install Python package manager and development tools
set -e

echo "🐍 Installing Python tools..."

# Install uv (modern Python package manager)
echo "🔄 Installing uv Python package manager..."
python3 -m pip install --user uv

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

echo "✅ Python tools installation completed"