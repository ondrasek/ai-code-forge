#!/bin/bash

set -e

[ -z $gpgAgentSocket ] && {
	echo "⚠️  No GPG agent socket provided. Skipping GPG Agent Socket configuration."
	exit 0
}

echo "🔐 Configuring GPG agent socket for shells..."

# Environment variables are loaded by postCreate.sh and exported to child processes

# Set up shell aliases and environment for bash
echo "📝 Adding GPG configuration to ~/.bashrc..."
cat >> ~/.bashrc << EOF

# GPG Agent Socket
export GPG_AGENT_INFO=
export GPG_TTY=$(tty)
export GNUPGHOME=/home/vscode/.gnupg
EOF

echo "📝 Adding GPG configuration to ~/.zshrc..."
cat >> ~/.zshrc << EOF

# GPG Agent Socket
export GPG_AGENT_INFO=
export GPG_TTY=$(tty)
export GNUPGHOME=/home/vscode/.gnupg
EOF

# Create agent symlink and GNUPGHOME
echo "📁 Creating GPG home directory..."
mkdir -p /home/vscode/.gnupg

echo "🔗 Setting up GPG agent socket symlink..."
[ -r /home/vscode/.gnupg/S.gpg-agent.extra ] || ln -sf /tmp/S.gpg-agent.extra /home/vscode/.gnupg/S.gpg-agent.extra

echo "📋 GPG configuration directories:"
gpgconf --list-dirs

# ...this time with variable substitution

echo "✅ GPG agent socket configuration completed successfully!"