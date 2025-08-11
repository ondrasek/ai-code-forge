#!/bin/bash

# Configure shell environment (zsh + Oh My Zsh)
set -e

echo "🐚 Configuring shell environment..."

# Check if running in Codespaces (may have zsh pre-installed)
if [ "$RUNTIME_ENV" = "codespaces" ]; then
    echo "🌐 Codespaces: Checking for pre-installed zsh..."
    if command -v zsh >/dev/null 2>&1; then
        echo "✅ zsh already installed in Codespaces"
    else
        echo "🔄 Installing zsh in Codespaces..."
        sudo apt-get update && sudo apt-get install -y zsh
    fi
else
    # Install and configure zsh for DevContainer
    echo "🐳 DevContainer: Installing zsh shell environment..."
    sudo apt-get update && sudo apt-get install -y zsh
fi

# Set zsh as default shell (needed in both environments)
sudo chsh -s $(which zsh) $USER

# Install Oh My Zsh for better zsh experience (needed in both environments)
if [ ! -d "$HOME/.oh-my-zsh" ]; then
    echo "🎨 Installing Oh My Zsh via secure git clone..."
    git clone https://github.com/ohmyzsh/ohmyzsh.git "$HOME/.oh-my-zsh"
    # Create zsh configuration from template
    cp "$HOME/.oh-my-zsh/templates/zshrc.zsh-template" "$HOME/.zshrc"
    # Set ZSH environment variable
    echo 'export ZSH="$HOME/.oh-my-zsh"' >> "$HOME/.zshrc"
    echo 'source $ZSH/oh-my-zsh.sh' >> "$HOME/.zshrc"
else
    echo "✅ Oh My Zsh already installed"
fi

echo "✅ Shell configuration completed"