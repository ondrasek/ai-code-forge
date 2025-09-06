#!/bin/bash

# Install and setup zsh shell
set -e

echo "🐚 Installing zsh shell..."

# Install zsh if not present
if command -v zsh >/dev/null 2>&1; then
    echo "✅ zsh already installed"
else
    echo "🔄 Installing zsh..."
    sudo apt-get install -y zsh
fi

# Set zsh as default shell (needed in both environments)
sudo chsh -s $(which zsh) $USER

echo "✅ Zsh installation completed"