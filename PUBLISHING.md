# Publishing Guide for Ollama Agents SDK

This guide will help you publish the package to PyPI.

## Prerequisites

### 1. Install Build Tools

```bash
pip install --upgrade pip build twine
```

### 2. Create PyPI Account

1. Go to https://pypi.org/account/register/
2. Verify your email
3. Set up 2FA (recommended)

### 3. Create API Token

1. Go to https://pypi.org/manage/account/token/
2. Create a new API token
3. Scope: "Entire account" (for first upload) or specific project
4. Save the token securely (you'll only see it once)

## Pre-Publishing Checklist

### Update Version Numbers

Make sure version is consistent across files:
- [ ] `setup.py` - version="0.2.0"
- [ ] `pyproject.toml` - version = "0.2.0"
- [ ] `CHANGELOG.md` - ## [0.2.0]

### Update Package Info

- [ ] `setup.py` - Update author_email, url
- [ ] `pyproject.toml` - Update email, URLs
- [ ] `README.md` - Up to date with features
- [ ] `CHANGELOG.md` - Document all changes

### Clean Up

```bash
# Remove old build artifacts
rm -rf dist/ build/ *.egg-info

# Remove test databases and caches
rm -f *.db
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Check code formatting
black --check ollama_agents/

# Check for issues
flake8 ollama_agents/ --max-line-length=100
```

## Building the Package

### 1. Build Distribution Files

```bash
python -m build
```

This creates:
- `dist/ollama_agents_sdk-0.2.0-py3-none-any.whl` (wheel)
- `dist/ollama-agents-sdk-0.2.0.tar.gz` (source)

### 2. Check the Build

```bash
twine check dist/*
```

Should show:
```
Checking dist/ollama_agents_sdk-0.2.0-py3-none-any.whl: PASSED
Checking dist/ollama-agents-sdk-0.2.0.tar.gz: PASSED
```

### 3. Test Installation Locally

```bash
# Create a test environment
python -m venv test_env
source test_env/bin/activate

# Install from local build
pip install dist/ollama_agents_sdk-0.2.0-py3-none-any.whl

# Test import
python -c "from ollama_agents import Agent; print('Success!')"

# Deactivate and remove
deactivate
rm -rf test_env
```

## Publishing to PyPI

### Option 1: Test PyPI First (Recommended)

```bash
# Upload to Test PyPI
twine upload --repository testpypi dist/*

# When prompted, use:
# Username: __token__
# Password: <your-testpypi-token>
```

Test the installation:
```bash
pip install --index-url https://test.pypi.org/simple/ ollama-agents-sdk
```

### Option 2: Publish to Production PyPI

```bash
# Upload to PyPI
twine upload dist/*

# When prompted, use:
# Username: __token__
# Password: <your-pypi-token>
```

### Using ~/.pypirc (Optional)

Create `~/.pypirc` to avoid entering credentials:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE

[testpypi]
username = __token__
password = pypi-YOUR_TESTPYPI_TOKEN_HERE
repository = https://test.pypi.org/legacy/
```

Then upload with:
```bash
twine upload --repository testpypi dist/*
```

## Post-Publishing

### 1. Verify on PyPI

Visit: https://pypi.org/project/ollama-agents-sdk/

Check:
- [ ] Package name and version correct
- [ ] README displays properly
- [ ] Links work
- [ ] Classifiers correct

### 2. Test Installation

```bash
pip install ollama-agents-sdk

# Or specific version
pip install ollama-agents-sdk==0.2.0
```

### 3. Create Git Tag

```bash
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0
```

### 4. Create GitHub Release

1. Go to your repository on GitHub
2. Click "Releases" > "Create a new release"
3. Choose tag v0.2.0
4. Title: "v0.2.0"
5. Description: Copy from CHANGELOG.md
6. Attach dist files (optional)
7. Publish release

## Updating the Package

For subsequent releases:

1. Make your changes
2. Update version in `setup.py` and `pyproject.toml`
3. Update `CHANGELOG.md`
4. Clean, build, and test
5. Upload to PyPI
6. Tag and create GitHub release

## Common Issues

### "File already exists"

If you try to upload the same version twice:
```
ERROR: File already exists
```

**Solution**: Increment the version number and rebuild.

### Import Errors

If imports fail after installation:
```python
ModuleNotFoundError: No module named 'ollama_agents'
```

**Solutions**:
- Check `packages` in setup.py includes "ollama_agents"
- Verify `__init__.py` exists in ollama_agents/
- Check for typos in package name

### Missing Dependencies

If dependencies aren't installing:

**Solution**: Check requirements.txt is included in MANIFEST.in

### README Not Displaying

If README doesn't show on PyPI:

**Solution**: Verify `long_description_content_type="text/markdown"` in setup.py

## Quick Reference

### Build and Publish Commands

```bash
# Clean
rm -rf dist/ build/ *.egg-info

# Build
python -m build

# Check
twine check dist/*

# Test PyPI
twine upload --repository testpypi dist/*

# Production PyPI
twine upload dist/*
```

### Version Update Checklist

- [ ] Increment version in setup.py
- [ ] Increment version in pyproject.toml
- [ ] Add entry to CHANGELOG.md
- [ ] Commit changes
- [ ] Build and test
- [ ] Publish
- [ ] Create git tag
- [ ] Create GitHub release

## Resources

- PyPI: https://pypi.org/
- Test PyPI: https://test.pypi.org/
- Packaging Guide: https://packaging.python.org/
- Twine Docs: https://twine.readthedocs.io/

## Support

For issues with publishing:
- Check PyPI status: https://status.python.org/
- PyPI help: https://pypi.org/help/
- Packaging discussions: https://discuss.python.org/c/packaging/14
