#!/bin/bash

echo "================================================================================"
echo "🏷️  CREATE GIT TAG AND GITHUB RELEASE"
echo "================================================================================"
echo ""

# Create tag
echo "Creating git tag v0.2.0..."
git tag -a v0.2.0 -m "Release version 0.2.0

Features:
- Multi-agent collaboration
- Tool calling with automatic execution  
- DuckDuckGo web search (no API keys!)
- Qdrant vector store integration
- Memory backends (SQLite, Qdrant)
- Comprehensive logging and tracing
- Agent handoffs
- Statistics tracking"

if [ $? -eq 0 ]; then
    echo "✅ Tag created"
else
    echo "❌ Tag creation failed (may already exist)"
fi

# Push tag
echo ""
echo "Pushing tag to GitHub..."
git push origin v0.2.0

if [ $? -eq 0 ]; then
    echo "✅ Tag pushed to GitHub"
else
    echo "❌ Push failed"
    exit 1
fi

echo ""
echo "================================================================================"
echo "✅ TAG CREATED AND PUSHED"
echo "================================================================================"
echo ""
echo "Now create GitHub Release:"
echo "1. Go to: https://github.com/SlyWolf1/ollama-agent/releases/new"
echo "2. Choose tag: v0.2.0"
echo "3. Title: v0.2.0 - Multi-Agent Collaboration & DuckDuckGo Search"
echo "4. Description: Copy from CHANGELOG.md"
echo "5. Attach files:"
echo "   - dist/ollama_agents_sdk-0.2.0-py3-none-any.whl"
echo "   - dist/ollama_agents_sdk-0.2.0.tar.gz"
echo "6. Publish release"
echo ""

