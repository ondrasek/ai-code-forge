#!/bin/bash

set -e

[ -z $sshAuthSock ] && {
	echo No SSH agent socket provided. Skipping SSH Agent Socket configuration.
	exit 0
}

echo "🔧 Configuring shells to set SSH_AUTH_SOCK..."

# Environment variables are loaded by postCreate.sh and exported to child processes

# Set up shell aliases and environment for bash
cat >> ~/.bashrc << EOF

# SSH_AUTH_SOCK
export SSH_AUTH_SOCK=$sshAuthSock
EOF

cat >> ~/.zshrc << EOF

# SSH_AUTH_SOCK
export SSH_AUTH_SOCK=$sshAuthSock
EOF

# ...this time with variable substitution

echo "✅ "
