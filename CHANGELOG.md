# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-12-30

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

## [0.1.0] - 2024-XX-XX

### Added
- Initial release
- Basic agent implementation
- Tool calling support
- Memory backends (SQLite, Qdrant)
- Web search integration
- Handoff manager
- Statistics tracking
- Tracing and logging

[0.2.0]: https://github.com/yourusername/ollama-agents-sdk/releases/tag/v0.2.0
[0.1.0]: https://github.com/yourusername/ollama-agents-sdk/releases/tag/v0.1.0
