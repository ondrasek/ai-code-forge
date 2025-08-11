#!/bin/bash
set -e

echo "🤖 Configuring Claude Code..."

# Check if CLAUDE_CODE_OAUTH_TOKEN is available
if [ -z "$CLAUDE_CODE_OAUTH_TOKEN" ]; then
    echo "⚠️  CLAUDE_CODE_OAUTH_TOKEN not found in environment"
    echo "   To avoid the setup wizard on each rebuild:"
    echo "   1. Run 'claude setup-token' on your host machine"
    echo "   2. Add the token to your .env file"
    echo "   3. Rebuild the devcontainer"
    echo "   See .env.template for details."
    exit 0
fi

# Create Claude configuration directory
mkdir -p ~/.claude

# Create user-level configuration to bypass setup wizard
echo "📝 Creating Claude Code user configuration..."

# Generate unique user ID and timestamp for configuration
USER_ID=$(uuidgen 2>/dev/null || echo "devcontainer-$(date +%s)")
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")

# Create ~/.claude.json with wizard bypass settings
cat > ~/.claude.json << EOF
{
  "userId": "$USER_ID",
  "projects": {
    "/workspace": {
      "hasTrustDialogAccepted": true,
      "hasTrustDialogHooksAccepted": true,
      "hasCompletedProjectOnboarding": true,
      "projectOnboardingSeenCount": 1,
      "hasClaudeMdExternalIncludesApproved": true,
      "createdAt": "$TIMESTAMP",
      "lastUsed": "$TIMESTAMP"
    }
  },
  "globalSettings": {
    "hasWelcomeDialogShown": true,
    "hasInitialSetupCompleted": true,
    "defaultPermissionMode": "bypassPermissions"
  },
  "authentication": {
    "hasCompletedOAuth": true,
    "lastAuthCheck": "$TIMESTAMP"
  }
}
EOF

# Set proper permissions
chmod 600 ~/.claude.json

# Verify Claude Code authentication
echo "🔐 Verifying Claude Code authentication..."
if claude config list >/dev/null 2>&1; then
    echo "✅ Claude Code authentication successful"
else
    echo "⚠️  Claude Code authentication verification failed"
    echo "   This is expected if Claude Code is not yet installed"
fi

echo "✅ Claude Code configuration completed"
echo "   - Trust dialogs: Pre-accepted for /workspace"
echo "   - Permissions: Set to bypass mode"  
echo "   - Setup wizard: Will be bypassed on first run"