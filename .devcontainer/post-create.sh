#!/bin/bash

# Post-create script for devcontainer setup
# This script runs after the container is created

echo "🚀 Running post-create setup..."

# Install Claude Code globally
echo "📦 Installing Claude Code..."
npm install -g @anthropic-ai/claude-code

# Install Node.js dependencies for website
echo "📦 Installing Node.js dependencies..."
cd website && npm install && cd ..

# Install Python dependencies for agents service
echo "🐍 Installing Python dependencies..."
pip install -r agents-service/requirements.txt

# Create output directory for generated games
echo "📁 Creating output directories..."
mkdir -p /workspaces/lovable-clone/agents-service/generated_games

# Make sure the agents service directory exists
mkdir -p /workspaces/lovable-clone/agents-service

echo "🎉 Post-create setup complete!"
echo ""
echo "📋 Available services:"
echo "  • Start everything: cd website && npm run dev:full"
echo "  • Next.js website only: cd website && npm run dev"
echo "  • Chainlit agent only: cd website && npm run agents:start"
echo "  • FastAPI only: cd website && npm run agents:api"
echo ""
echo "🔧 Don't forget to:"
echo "  • Set OPENAI_API_KEY in agents-service/.env"
echo "  • Set ANTHROPIC_API_KEY in agents-service/.env (optional)"
