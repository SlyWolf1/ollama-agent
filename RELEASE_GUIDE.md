# Release Guide - Ollama Agents SDK v0.2.0

## ✅ What's Been Done

### 1. Git Repository Setup ✅
- [x] Git repository initialized
- [x] Initial commit created
- [x] Main branch created
- [x] Dev branch created
- [x] Remote configured: https://github.com/SlyWolf1/ollama-agent.git

### 2. Package Built ✅
- [x] Old builds cleaned
- [x] Package built successfully
- [x] Build checks passed
- [x] Files created:
  - `dist/ollama_agents_sdk-0.2.0-py3-none-any.whl` (45KB)
  - `dist/ollama_agents_sdk-0.2.0.tar.gz` (70KB)

### 3. Scripts Created ✅
- [x] `git_push.sh` - Push to GitHub
- [x] `publish_testpypi.sh` - Publish to Test PyPI
- [x] `publish_pypi.sh` - Publish to Production PyPI
- [x] `create_release.sh` - Create Git tag and release

## 🚀 Release Steps

### Step 1: Push to GitHub

```bash
./git_push.sh
```

**Authentication Options:**

**Option A: Personal Access Token (Recommended)**
1. Create token: https://github.com/settings/tokens
2. Select scope: `repo` (full control)
3. Use token as password (username: your GitHub username)

**Option B: SSH**
```bash
git remote set-url origin git@github.com:SlyWolf1/ollama-agent.git
./git_push.sh
```

This will:
- Push main branch (force)
- Push dev branch (force)

### Step 2: Publish to Test PyPI (Recommended)

```bash
./publish_testpypi.sh
```

**Prerequisites:**
1. Test PyPI account: https://test.pypi.org/account/register/
2. API token: https://test.pypi.org/manage/account/token/
   - Scope: "Entire account"
   - Save the token

**When prompted:**
- Username: `__token__`
- Password: `<your-testpypi-token>`

**Test the installation:**
```bash
pip install --index-url https://test.pypi.org/simple/ ollama-agents-sdk
python -c "from ollama_agents import Agent; print('✅ Works!')"
```

### Step 3: Publish to Production PyPI

```bash
./publish_pypi.sh
```

**Prerequisites:**
1. PyPI account: https://pypi.org/account/register/
2. API token: https://pypi.org/manage/account/token/
   - Scope: "Entire account" or specific to this project
   - Save the token

**When prompted:**
- Confirm: `yes`
- Username: `__token__`
- Password: `<your-pypi-token>`

After success, your package will be available:
```bash
pip install ollama-agents-sdk
```

### Step 4: Create GitHub Release

```bash
./create_release.sh
```

This will:
- Create git tag `v0.2.0`
- Push tag to GitHub

Then manually create the release:
1. Go to: https://github.com/SlyWolf1/ollama-agent/releases/new
2. Choose tag: `v0.2.0`
3. Title: `v0.2.0 - Multi-Agent Collaboration & DuckDuckGo Search`
4. Description: Copy from `CHANGELOG.md`
5. Attach files:
   - `dist/ollama_agents_sdk-0.2.0-py3-none-any.whl`
   - `dist/ollama_agents_sdk-0.2.0.tar.gz`
6. Click "Publish release"

## 📦 Package Information

**Name:** ollama-agents-sdk  
**Version:** 0.2.0  
**Author:** Brian Manda <brianmanda44@gmail.com>  
**GitHub:** https://github.com/SlyWolf1/ollama-agent  
**License:** MIT  

## 🎯 Key Features

- Multi-Agent Collaboration
- Tool Calling (automatic execution)
- DuckDuckGo Web Search (no API keys!)
- Qdrant Vector Store integration
- Memory backends (SQLite, Qdrant, Redis, PostgreSQL)
- Comprehensive logging and tracing
- Agent handoffs
- Statistics tracking

## 📊 Release Checklist

- [x] Git repository initialized
- [x] Branches created (main, dev)
- [ ] Code pushed to GitHub
- [ ] Published to Test PyPI
- [ ] Tested installation from Test PyPI
- [ ] Published to Production PyPI
- [ ] Git tag created
- [ ] GitHub release created
- [ ] Announcement made

## 🔧 Troubleshooting

### Git Push Issues

**Problem:** Authentication failed  
**Solution:** Use Personal Access Token instead of password

**Problem:** Remote already exists  
**Solution:** 
```bash
git remote remove origin
git remote add origin https://github.com/SlyWolf1/ollama-agent.git
```

### PyPI Upload Issues

**Problem:** "File already exists"  
**Solution:** Version 0.2.0 already uploaded. Increment version.

**Problem:** "Invalid username/password"  
**Solution:** Use `__token__` as username and API token as password

**Problem:** "Package name not available"  
**Solution:** Someone else might have the name. Choose different name.

### GitHub Release Issues

**Problem:** Can't create tag  
**Solution:** Tag might already exist. Delete it first:
```bash
git tag -d v0.2.0
git push origin :refs/tags/v0.2.0
```

## 📞 Support

- GitHub Issues: https://github.com/SlyWolf1/ollama-agent/issues
- Email: brianmanda44@gmail.com

## 🎉 After Release

After successful release:

1. **Announce on social media**
   - Twitter/X
   - Reddit (r/LocalLLaMA, r/Python)
   - LinkedIn

2. **Update documentation**
   - Add examples
   - Create tutorials
   - Update README if needed

3. **Monitor feedback**
   - Check GitHub issues
   - Respond to questions
   - Fix bugs

4. **Plan next version**
   - Collect feature requests
   - Plan improvements
   - Update roadmap

---

**Good luck with your release! 🚀**
