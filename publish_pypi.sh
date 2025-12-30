#!/bin/bash

echo "================================================================================"
echo "🚀 PUBLISH TO PYPI (PRODUCTION)"
echo "================================================================================"
echo ""
echo "⚠️  WARNING: This will publish to PRODUCTION PyPI!"
echo ""
echo "Make sure you have:"
echo "1. Tested on Test PyPI"
echo "2. PyPI account: https://pypi.org/account/register/"
echo "3. API token: https://pypi.org/manage/account/token/"
echo ""
read -p "Are you sure you want to publish? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Uploading to PyPI..."
twine upload dist/*

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================================"
    echo "🎉 PUBLISHED TO PYPI!"
    echo "================================================================================"
    echo ""
    echo "Your package is now live!"
    echo ""
    echo "Install it:"
    echo "  pip install ollama-agents-sdk"
    echo ""
    echo "View on PyPI:"
    echo "  https://pypi.org/project/ollama-agents-sdk/"
    echo ""
    echo "Next steps:"
    echo "1. Create git tag: git tag -a v0.2.0 -m 'Release v0.2.0'"
    echo "2. Push tag: git push origin v0.2.0"
    echo "3. Create GitHub release: https://github.com/SlyWolf1/ollama-agent/releases"
    echo ""
else
    echo ""
    echo "❌ Upload failed"
    exit 1
fi

