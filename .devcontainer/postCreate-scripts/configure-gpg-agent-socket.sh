#!/bin/bash

set -e

[ -z $gpgAgentSocket ] && {
	echo No SSH agent socket provided. Skipping SSH Agent Socket configuration.
	exit 0
}

echo "🔧 Configuring shells to set SSH_AUTH_SOCK..."

# Environment variables are loaded by postCreate.sh and exported to child processes

# Set up shell aliases and environment for bash
cat >> ~/.bashrc << EOF

# GPG Agent Socket
export GPG_AGENT_INFO=
export GPG_TTY=$(tty)
export GNUPGHOME=/home/vscode/.gnupg
EOF

cat >> ~/.zshrc << EOF

# GPG Agent Socket
export GPG_AGENT_INFO=
export GPG_TTY=$(tty)
export GNUPGHOME=/home/vscode/.gnupg
EOF

# Create agent symlink and GNUPGHOME
mkdir -p /home/vscode/.gnupg
[ -r /home/vscode/.gnupg/S.gpg-agent.extra ] || ln -sf /tmp/S.gpg-agent.extra /home/vscode/.gnupg/S.gpg-agent.extra
gpgconf --list-dirs

# ...this time with variable substitution

echo "✅ "
