#!/bin/bash

# Clone and sync repository
set -e

# Skip in Codespaces (repository already available)
if [ "$CODESPACES" = "true" ]; then
    echo "🌐 Skipping repository clone - running in Codespaces"
    exit 0
fi

echo "📋 Cloning repository for DevContainer..."

echo "📋 Cloning repository into workspace:"
if [ -d $workingCopy/.git ]; then
  cd $workingCopy
  gh repo sync
  cd -
  echo "✅ Repository synced"
else
  gh repo clone ondrasek/ai-code-forge $workingCopy
  echo "✅ Repository cloned"
fi

echo "✅ Repository clone completed"