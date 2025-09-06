#!/bin/bash

# Setup shell navigation shortcuts
set -e

echo "🧭 Setting up shell navigation..."

# Create shell aliases and shortcuts for repository navigation
cat >> /home/vscode/.zshrc << 'EOF'

# Repository navigation shortcuts
alias repo='cd /workspace/test-repo'
alias worktrees='cd /workspace/worktrees/test-repo'

EOF

cat >> /home/vscode/.bashrc << 'EOF'

# Repository navigation shortcuts  
alias repo='cd /workspace/test-repo'
alias worktrees='cd /workspace/worktrees/test-repo'

EOF

# Change to repository directory by default
cd /workspace/test-repo

echo "✅ Shell navigation setup completed"