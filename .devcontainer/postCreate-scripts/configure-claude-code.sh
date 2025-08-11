#!/bin/bash

# Configure Claude Code to bypass setup wizard
set -e

echo "🎯 Configuring Claude Code preconfiguration..."

# Create Claude configuration directory
mkdir -p /home/vscode/.claude
mkdir -p /workspace/.claude

# Generate a unique user ID (required for config)
USER_ID=$(date +%s | sha256sum | head -c 32)
FIRST_START_TIME=$(date -u +"%Y-%m-%dT%H:%M:%S.000Z")

# Create main Claude configuration file with wizard bypass settings
cat > /home/vscode/.claude.json << EOF
{
  "installMethod": "npm",
  "autoUpdates": true,
  "firstStartTime": "${FIRST_START_TIME}",
  "userID": "${USER_ID}",
  "projects": {
    "/workspace": {
      "allowedTools": [],
      "history": [],
      "mcpContextUris": [],
      "mcpServers": {},
      "enabledMcpjsonServers": [],
      "disabledMcpjsonServers": [],
      "hasTrustDialogAccepted": true,
      "hasTrustDialogHooksAccepted": true,
      "projectOnboardingSeenCount": 1,
      "hasClaudeMdExternalIncludesApproved": true,
      "hasClaudeMdExternalIncludesWarningShown": true,
      "hasCompletedProjectOnboarding": true
    }
  },
  "fallbackAvailableWarningThreshold": 0.5
}
EOF

# Create project-specific settings for permission bypass
cat > /workspace/.claude/settings.json << EOF
{
  "model": "claude-sonnet-4-20250514",
  "permissions": {
    "defaultMode": "bypassPermissions"
  },
  "includeCoAuthoredBy": true,
  "cleanupPeriodDays": 30
}
EOF

# Set proper ownership and permissions
chown vscode:vscode /home/vscode/.claude.json
chown vscode:vscode /workspace/.claude/settings.json
chmod 600 /home/vscode/.claude.json
chmod 644 /workspace/.claude/settings.json

echo "✅ Claude Code preconfiguration completed"
echo "   - Wizard bypass configured"
echo "   - Trust dialogs pre-accepted"
echo "   - Permission bypass enabled"
echo "   - Project onboarding marked complete"

# Note about authentication
if [ -z "${CLAUDE_CODE_OAUTH_TOKEN}" ]; then
    echo "ℹ️  Authentication: Set CLAUDE_CODE_OAUTH_TOKEN environment variable"
    echo "   Add to your .env file or devcontainer environment"
fi