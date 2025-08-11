#!/bin/bash

# Configure Claude Code user-level settings to bypass setup wizard
set -e

echo "🤖 Configuring Claude Code user settings..."

# Create Claude config directory if it doesn't exist
mkdir -p ~/.claude

# Create user configuration to bypass setup wizard
# This configuration is stored at user level (~/.claude.json) and does not modify repository settings
cat > ~/.claude.json << 'EOF'
{
  "projects": {
    "/workspace": {
      "hasTrustDialogAccepted": true,
      "hasTrustDialogHooksAccepted": true,
      "hasCompletedProjectOnboarding": true,
      "projectOnboardingSeenCount": 1,
      "hasClaudeMdExternalIncludesApproved": true
    }
  },
  "hasCompletedGlobalOnboarding": true,
  "globalOnboardingSeenCount": 1,
  "permissions": {
    "defaultMode": "bypassPermissions"
  },
  "hasAcceptedTerms": true,
  "lastUsedWorkspace": "/workspace"
}
EOF

# Set proper permissions
chmod 600 ~/.claude.json
chown vscode:vscode ~/.claude.json

# If Claude Code OAuth token is available from environment, use it for authentication
if [ -n "$CLAUDE_CODE_OAUTH_TOKEN" ]; then
    echo "🔐 Setting up Claude Code authentication from environment variable"
    # Export for current session
    export CLAUDE_CODE_OAUTH_TOKEN="$CLAUDE_CODE_OAUTH_TOKEN"
    
    # Add to shell profile for future sessions
    if ! grep -q "CLAUDE_CODE_OAUTH_TOKEN" ~/.zshrc 2>/dev/null; then
        echo "export CLAUDE_CODE_OAUTH_TOKEN=\"\$CLAUDE_CODE_OAUTH_TOKEN\"" >> ~/.zshrc
    fi
    if ! grep -q "CLAUDE_CODE_OAUTH_TOKEN" ~/.bashrc 2>/dev/null; then
        echo "export CLAUDE_CODE_OAUTH_TOKEN=\"\$CLAUDE_CODE_OAUTH_TOKEN\"" >> ~/.bashrc
    fi
else
    echo "⚠️  CLAUDE_CODE_OAUTH_TOKEN not set - authentication will need to be configured manually"
    echo "   To set up authentication, add CLAUDE_CODE_OAUTH_TOKEN to your .env file"
fi

echo "✅ Claude Code user configuration completed"
echo "   - Configuration wizard will be bypassed"
echo "   - Trust dialogs pre-accepted for /workspace"
echo "   - Permissions set to bypass mode"
echo "   - Repository-level settings preserved as recommended defaults"