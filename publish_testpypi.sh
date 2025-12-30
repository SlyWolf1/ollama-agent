#!/bin/bash

echo "================================================================================"
echo "📦 PUBLISH TO TEST PYPI"
echo "================================================================================"
echo ""
echo "This will upload your package to Test PyPI for testing."
echo ""
echo "Prerequisites:"
echo "1. Test PyPI account: https://test.pypi.org/account/register/"
echo "2. API token: https://test.pypi.org/manage/account/token/"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

echo ""
echo "Uploading to Test PyPI..."
twine upload --repository testpypi dist/*

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================================"
    echo "✅ UPLOADED TO TEST PYPI"
    echo "================================================================================"
    echo ""
    echo "Test your package:"
    echo "  pip install --index-url https://test.pypi.org/simple/ ollama-agents-sdk"
    echo ""
    echo "View on Test PyPI:"
    echo "  https://test.pypi.org/project/ollama-agents-sdk/"
    echo ""
else
    echo ""
    echo "❌ Upload failed"
    echo ""
    echo "Common issues:"
    echo "• Make sure you have a Test PyPI account"
    echo "• Use API token as password (username: __token__)"
    echo "• Check if version 0.2.0 already exists"
    echo ""
fi

