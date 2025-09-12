#!/bin/bash

# Update and upgrade system packages
set -e

echo "📦 Updating system packages..."

# Update package lists and upgrade packages
echo "🔄 Updating package lists and installing security updates..."
sudo apt-get update && sudo apt-get upgrade -y

echo "✅ System packages updated successfully"