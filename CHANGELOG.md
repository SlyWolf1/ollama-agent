# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2024-12-31

### 🎉 Major Updates

#### Logging System Overhaul
- **Logging disabled by default** for better performance in production
- New `enable_logging()` and `disable_logging()` functions
- Configurable log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Call `enable_logging()` and `set_global_log_level(LogLevel.DEBUG)` to enable detailed logging

#### Consolidated Agent Implementation  
- Fully integrated enhanced_agent.py features into agent.py
- Single, unified Agent class with all capabilities
- Removed code duplication and improved maintainability
- Better separation of concerns

#### Improved Multi-Agent Collaboration
- Fixed critical agent handoff response propagation issues
- Specialized agents now properly return responses to coordinator
- Enhanced triage agent instructions for better routing
- New `simple_collaborative_agents.py` production-ready example
- Tool results are properly shown to users

#### Model Configuration
- Default model: `qwen2.5-coder:3b-instruct-q8_0` (fast, efficient)
- User-specified models are properly honored throughout
- Thinking mode is now optional (disabled by default)
- Only enable thinking for models that support it
- No hardcoded model references

#### Web Search Improvements
- Complete DuckDuckGo + Playwright integration
- No API keys required!
- Synchronous and asynchronous search methods
- Better error handling with helpful installation messages
- Robust search result extraction

### 📚 Documentation
- Completely rewritten README with 600+ lines of examples
- Comprehensive usage guide for all features
- Best practices section
- Troubleshooting guide
- Added logging configuration examples
- Removed redundant markdown files (PUBLISHING.md, RELEASE_GUIDE.md, etc.)

### 🔧 Features
- Enhanced tool execution with detailed logging
- Better error messages and debugging information
- Improved response handling in agent handoffs
- Statistics tracking for performance monitoring
- Memory management across multiple backends
- Built-in tool collections
- Agent orchestration patterns

### 🐛 Bug Fixes
- Fixed agent handoff responses not showing to end user
- Fixed tool calling failures with certain models
- Fixed logging always being enabled (major performance issue)
- Fixed model parameter being overridden incorrectly
- Fixed thinking mode causing errors on unsupported models
- Fixed web search agent not returning proper responses

### 📦 Examples
- New `simple_collaborative_agents.py` - Clean, production-ready example
- Updated `collaborative_agents_example.py` with all fixes and improvements
- Better structured examples with clear documentation
- Removed duplicate and outdated examples

### ⚡ Performance
- Eliminated logging overhead when disabled (significant improvement)
- Faster agent initialization
- Reduced memory footprint
- Better resource management

### 🔨 Breaking Changes
- **Logging must be explicitly enabled** (was on by default in 0.2.0)
- Default model changed from `llama3.2` to `qwen2.5-coder:3b-instruct-q8_0`
- Removed some redundant markdown documentation files
- `enhanced_agent.py` removed (features merged into `agent.py`)

### 📝 Migration Guide from 0.2.0

#### Enable Logging (if needed)
```python
# Old (0.2.0) - logging was always on, causing performance issues
from ollama_agents import Agent

# New (0.3.0) - must enable explicitly for development/debugging
from ollama_agents import Agent, enable_logging, set_global_log_level, LogLevel

enable_logging()
set_global_log_level(LogLevel.INFO)  # or DEBUG for verbose output
```

#### Model Selection
```python
# Specify your model explicitly (default is qwen2.5-coder:3b-instruct-q8_0)
agent = Agent(
    name="my_agent",
    model="qwen2.5-coder:3b-instruct-q8_0",  # or any Ollama model
    instructions="You are helpful."
)
```

#### Thinking Mode (Optional)
```python
from ollama_agents import Agent, ModelSettings, ThinkingMode

# Only use with models that support thinking
agent = Agent(
    name="thinker",
    model="deepseek-r1:latest",  # Must support thinking
    settings=ModelSettings(
        thinking_mode=ThinkingMode.MEDIUM  # Optional, disabled by default
    )
)
```

## [0.2.0] - 2024-12-30

### Added
- DuckDuckGo web search using Playwright (no API keys needed!)
- Multi-round tool execution loop for complex agent interactions
- JSON parser fallback for models that don't support native tool calling
- Comprehensive logging throughout the agent system
- Agent handoff responses now show full LLM responses including errors
- Triage agent for coordinating multiple specialized agents
- File search agent with Qdrant vector store integration
- Web search agent with DuckDuckGo integration
- Collaborative multi-agent examples
- **Advanced orchestration patterns**: Sequential, Parallel, Hierarchical, Consensus, Debate, Pipeline
- **Web UI** for agent management with Flask
- **Built-in tools**: File, Web, System, Data, and Text tools
- **Performance optimizations**: LRU cache, request batching, connection pooling, response caching
- **New memory backends**: MongoDB and JSON file storage
- 20+ ready-to-use tools across 5 categories
- AgentOrchestrator for coordinating multiple agents
- AgentManager for web UI agent management

### Changed
- Merged `agent.py` and `enhanced_agent.py` into single unified agent
- Default model changed to `qwen2.5-coder:3b-instruct-q8_0`
- Thinking mode now opt-in (disabled by default)
- Model configuration honors user settings (no hardcoded models)
- Tool execution now properly handles and processes results
- Enhanced error messages and transparency in agent handoffs

### Fixed
- Tool execution bug where tools weren't being called
- Models returning JSON text instead of proper tool calls
- Agent handoffs not showing full responses
- Thinking mode causing errors on unsupported models

### Removed
- Hardcoded `llama3.2` references
- Dependency on Brave Search API
- `enhanced_agent.py` (merged into `agent.py`)

## [0.1.0] - 2024-12-15

### Added
- Initial release
- Basic agent implementation
- Tool calling support
- Memory backends (SQLite, Qdrant)
- Web search integration
- Handoff manager
- Statistics tracking
- Tracing and logging

[0.3.0]: https://github.com/SlyWolf1/ollama-agent/releases/tag/v0.3.0
[0.2.0]: https://github.com/SlyWolf1/ollama-agent/releases/tag/v0.2.0
[0.1.0]: https://github.com/SlyWolf1/ollama-agent/releases/tag/v0.1.0
