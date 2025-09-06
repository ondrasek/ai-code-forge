#!/bin/bash

# Install essential apt dependencies
set -e

echo "📦 Installing essential apt dependencies..."

# Update package lists first
echo "🔄 Updating package lists..."
sudo apt-get update

# Install gnupg if not present
if command -v gpg >/dev/null 2>&1; then
    echo "✅ gnupg already installed"
else
    echo "🔄 Installing gnupg..."
    sudo apt-get install -y gnupg
fi

# Add other essential dependencies here as needed
# Example pattern for future dependencies:
# if command -v <command> >/dev/null 2>&1; then
#     echo "✅ <package> already installed"
# else
#     echo "🔄 Installing <package>..."
#     sudo apt-get install -y <package>
# fi

echo "✅ Essential apt dependencies installation completed"