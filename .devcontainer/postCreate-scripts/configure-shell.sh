#!/bin/bash

# Configure shell environment (zsh + Oh My Zsh)
set -e

echo "🐚 Configuring shell environment..."

# Install and configure zsh
echo "🐚 Setting up zsh shell environment..."
sudo apt-get update && sudo apt-get install -y zsh

# Set zsh as default shell
sudo chsh -s $(which zsh) $USER

# Install Oh My Zsh for better zsh experience - Secure git clone method
if [ ! -d "$HOME/.oh-my-zsh" ]; then
    echo "🎨 Installing Oh My Zsh via secure git clone..."
    git clone https://github.com/ohmyzsh/ohmyzsh.git "$HOME/.oh-my-zsh"
    # Create zsh configuration from template
    cp "$HOME/.oh-my-zsh/templates/zshrc.zsh-template" "$HOME/.zshrc"
    # Set ZSH environment variable
    echo 'export ZSH="$HOME/.oh-my-zsh"' >> "$HOME/.zshrc"
    echo 'source $ZSH/oh-my-zsh.sh' >> "$HOME/.zshrc"
fi

echo "✅ Shell configuration completed"