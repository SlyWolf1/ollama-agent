#!/bin/bash

echo "================================================================================"
echo "🚀 GIT PUSH SCRIPT"
echo "================================================================================"
echo ""
echo "This script will push your code to GitHub."
echo "You'll need to authenticate with GitHub."
echo ""
echo "Options:"
echo "1. Use HTTPS with Personal Access Token (recommended)"
echo "2. Use SSH (if you have SSH keys set up)"
echo ""

# Check current remotes
echo "Current remote:"
git remote -v

echo ""
echo "Pushing to main branch..."
git push -u origin main --force

if [ $? -eq 0 ]; then
    echo "✅ Main branch pushed successfully"
else
    echo "❌ Failed to push main branch"
    exit 1
fi

echo ""
echo "Pushing to dev branch..."
git push -u origin dev --force

if [ $? -eq 0 ]; then
    echo "✅ Dev branch pushed successfully"
else
    echo "❌ Failed to push dev branch"
    exit 1
fi

echo ""
echo "================================================================================"
echo "✅ ALL BRANCHES PUSHED TO GITHUB"
echo "================================================================================"
echo ""
echo "View your repository at:"
echo "https://github.com/SlyWolf1/ollama-agent"
echo ""

