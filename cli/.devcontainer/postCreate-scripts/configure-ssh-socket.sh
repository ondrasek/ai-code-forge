#!/bin/bash

set -e

[ -z $sshAuthSock ] && {
	echo "⚠️  No SSH agent socket provided. Skipping SSH Agent Socket configuration."
	exit 0
}

echo "🔑 Configuring SSH agent socket for shells..."

# Environment variables are loaded by postCreate.sh and exported to child processes

# Set up shell aliases and environment for bash
echo "📝 Adding SSH configuration to ~/.bashrc..."
cat >> ~/.bashrc << EOF

# SSH_AUTH_SOCK
export SSH_AUTH_SOCK=$sshAuthSock
EOF

echo "📝 Adding SSH configuration to ~/.zshrc..."
cat >> ~/.zshrc << EOF

# SSH_AUTH_SOCK
export SSH_AUTH_SOCK=$sshAuthSock
EOF

# ...this time with variable substitution

echo "✅ SSH agent socket configuration completed successfully!"