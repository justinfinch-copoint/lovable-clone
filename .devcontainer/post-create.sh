#!/bin/bash

# Post-create script for devcontainer setup
# This script runs after the container is created

echo "🚀 Running post-create setup..."

# Install Claude Code globally
echo "📦 Installing Claude Code..."
npm install -g @anthropic-ai/claude-code

echo "🎉 Post-create setup complete!"
