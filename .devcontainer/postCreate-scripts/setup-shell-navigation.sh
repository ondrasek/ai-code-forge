#!/bin/bash

# Setup shell navigation shortcuts
set -e

echo "🧭 Setting up shell navigation..."

# Create shell aliases and shortcuts for repository navigation
cat >> /home/vscode/.zshrc << 'EOF'

# Repository navigation shortcuts
alias repo='cd /workspace/ai-code-forge'
alias worktrees='cd /workspace/worktrees/ai-code-forge'

EOF

cat >> /home/vscode/.bashrc << 'EOF'

# Repository navigation shortcuts  
alias repo='cd /workspace/ai-code-forge'
alias worktrees='cd /workspace/worktrees/ai-code-forge'

EOF

# Change to repository directory by default
cd /workspace/ai-code-forge

echo "✅ Shell navigation setup completed"