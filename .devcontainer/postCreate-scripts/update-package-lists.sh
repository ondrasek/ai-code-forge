#!/bin/bash

# Update package lists for package managers
set -e

echo "📦 Updating package lists..."

# Update apt package lists
echo "🔄 Updating apt package lists..."
sudo apt-get update

echo "✅ Package lists updated successfully"