#!/bin/bash

# Configure Claude Code at user level to bypass configuration wizard
# This script creates user-level configuration (~/.claude.json) instead of repository-level settings

set -e

echo "🤖 Configuring Claude Code (user-level)..."

# Check if CLAUDE_CODE_OAUTH_TOKEN is available
if [ -z "$CLAUDE_CODE_OAUTH_TOKEN" ]; then
    echo "⚠️  CLAUDE_CODE_OAUTH_TOKEN not found in environment"
    echo "    Claude Code will still be configured to bypass permission dialogs,"
    echo "    but you may need to authenticate manually on first run."
    echo "    Add CLAUDE_CODE_OAUTH_TOKEN to your .env file to avoid this."
fi

# Create Claude Code configuration directory
claude_user_dir="$HOME/.claude"
mkdir -p "$claude_user_dir"

# Create user-level Claude Code configuration
claude_config="$claude_user_dir/config.json" 

# Generate unique user ID for this devcontainer instance
user_id="devcontainer-$(date +%s)-$(whoami)"
current_timestamp=$(date -Iseconds)

cat > "$claude_config" << 'EOF'
{
  "projects": {},
  "userId": "$USER_ID",
  "firstRunTimestamp": "$CURRENT_TIMESTAMP",
  "lastActiveTimestamp": "$CURRENT_TIMESTAMP",
  "hasCompletedGlobalOnboarding": true,
  "globalOnboardingSeenCount": 1,
  "hasClaudeMdExternalIncludesApproved": true
}
EOF

# Substitute variables in the config file
sed -i "s/\$USER_ID/$user_id/g" "$claude_config"
sed -i "s/\$CURRENT_TIMESTAMP/$current_timestamp/g" "$claude_config"

# Create workspace-specific configuration to bypass all permission dialogs
workspace_config=$(cat << EOF
{
  "hasTrustDialogAccepted": true,
  "hasTrustDialogHooksAccepted": true,
  "hasCompletedProjectOnboarding": true,
  "projectOnboardingSeenCount": 1,
  "hasClaudeMdExternalIncludesApproved": true
}
EOF
)

# Add workspace-specific settings for the current workspace
workspace_path="/workspace"
python3 -c "
import json
import sys

config_file = '$claude_config'
workspace_path = '$workspace_path'
workspace_config = json.loads('$workspace_config')

# Load existing config
with open(config_file, 'r') as f:
    config = json.load(f)

# Add workspace-specific configuration
if 'projects' not in config:
    config['projects'] = {}

config['projects'][workspace_path] = workspace_config

# Write updated config
with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print(f'✅ Added workspace configuration for: {workspace_path}')
"

# Set proper permissions
chmod 644 "$claude_config"

echo "✅ Claude Code user-level configuration complete"
echo "   Configuration file: $claude_config"
echo "   Workspace: $workspace_path configured to bypass permission dialogs"