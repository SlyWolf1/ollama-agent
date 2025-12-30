#!/bin/bash
# Git Push and Release Script for v0.3.0

echo "=========================================="
echo "Git Push & Release - Ollama Agents SDK"
echo "Version: 0.3.0"
echo "=========================================="
echo ""

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"
echo ""

# Ensure we're on main
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "⚠️  Not on main branch. Switching to main..."
    git checkout main
fi

echo "📊 Git Status:"
git status --short
echo ""

# Push to GitHub
echo "🚀 Pushing to GitHub..."
echo ""
echo "Please authenticate with GitHub when prompted."
echo ""

read -p "Push to origin/main? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push origin main
    echo "✅ Pushed main branch"
    echo ""
    
    # Also push dev
    read -p "Push to origin/dev? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout dev
        git merge main -m "Sync dev with main for v0.3.0"
        git push origin dev
        git checkout main
        echo "✅ Pushed dev branch"
    fi
fi

echo ""
echo "=========================================="
echo "Build Status"
echo "=========================================="
echo ""

if [ -d "dist" ]; then
    echo "✅ Build files found in dist/:"
    ls -lh dist/
    echo ""
else
    echo "❌ No dist/ directory found"
    echo "Run: python3 -m build"
    exit 1
fi

echo ""
echo "=========================================="
echo "Next Steps"
echo "=========================================="
echo ""
echo "1. Create GitHub Release:"
echo "   - Go to: https://github.com/SlyWolf1/ollama-agent/releases/new"
echo "   - Tag: v0.3.0"
echo "   - Title: Ollama Agents SDK v0.3.0"
echo "   - Description: Copy from RELEASE_NOTES_v0.3.0.md"
echo "   - Attach: dist/ollama_agents_sdk-0.3.0.tar.gz"
echo "   - Attach: dist/ollama_agents_sdk-0.3.0-py3-none-any.whl"
echo ""
echo "2. Publish to PyPI (Test):"
echo "   python3 -m twine upload --repository testpypi dist/*"
echo ""
echo "3. Publish to PyPI (Production):"
echo "   python3 -m twine upload dist/*"
echo ""
echo "4. Verify Installation:"
echo "   pip install ollama-agents-sdk==0.3.0"
echo "   python3 -c 'import ollama_agents; print(ollama_agents.__version__)'"
echo ""
echo "=========================================="
echo "Done! ✨"
echo "=========================================="
