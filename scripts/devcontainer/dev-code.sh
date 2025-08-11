#!/bin/bash

# dev-code.sh - Simple wrapper for launching VS Code in DevContainer
# Usage: dev-code [directory]
#
# This is a simplified wrapper around vscode-launch.sh for quick access

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VSCODE_LAUNCH="$SCRIPT_DIR/vscode-launch.sh"

# Check if main script exists
if [[ ! -x "$VSCODE_LAUNCH" ]]; then
    echo "❌ ERROR: vscode-launch.sh not found or not executable at $VSCODE_LAUNCH"
    exit 1
fi

# Pass all arguments to the main script
exec "$VSCODE_LAUNCH" "$@"