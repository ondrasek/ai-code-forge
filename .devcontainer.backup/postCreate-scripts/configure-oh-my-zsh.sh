#!/bin/bash

# Configure Oh My Zsh for enhanced zsh experience
set -e

echo "🎨 Configuring Oh My Zsh..."

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

echo "✅ Oh My Zsh configuration completed"