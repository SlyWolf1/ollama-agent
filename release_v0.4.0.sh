#!/bin/bash
# Release script for Ollama Agents SDK v0.4.0

set -e  # Exit on error

echo "=================================="
echo "Ollama Agents SDK v0.4.0 Release"
echo "=================================="
echo ""

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "⚠️  Warning: Not on main branch (currently on $CURRENT_BRANCH)"
    echo "Switching to main..."
    git checkout main
fi

echo "📦 Step 1: Clean build artifacts"
rm -rf dist/ build/ *.egg-info ollama_agents_sdk.egg-info
echo "✅ Clean complete"
echo ""

echo "📦 Step 2: Build package"
python3 setup.py sdist
echo "✅ Build complete"
echo ""

echo "📊 Step 3: Check package"
ls -lh dist/
tar -tzf dist/ollama_agents_sdk-0.4.0.tar.gz | head -10
echo "..."
echo ""

echo "🔍 Step 4: Validate package (optional)"
echo "Run: python3 -m twine check dist/*"
echo ""

echo "=================================="
echo "✅ Package ready for release!"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Test on TestPyPI (recommended):"
echo "   python3 -m twine upload --repository testpypi dist/*"
echo ""
echo "2. Install and test:"
echo "   pip install --index-url https://test.pypi.org/simple/ ollama-agents-sdk"
echo ""
echo "3. Upload to production PyPI:"
echo "   python3 -m twine upload dist/*"
echo ""
echo "4. Push to GitHub:"
echo "   git push origin main dev"
echo ""
echo "5. Create GitHub release:"
echo "   gh release create v0.4.0 dist/* --title 'v0.4.0' --notes-file RELEASE_SUMMARY_v0.4.0.md"
echo ""
