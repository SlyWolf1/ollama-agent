# Ollama Agents SDK

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/ollama-agents-sdk.svg)](https://badge.fury.io/py/ollama-agents-sdk)

**Production-ready agent framework for Ollama with multi-agent collaboration, tool calling, web search, and advanced memory backends.**

Build intelligent AI agents that collaborate, use tools, search the web, and manage complex workflows - all powered by local Ollama models. Zero API keys required!

---

## ✨ Key Features

### 🤝 Multi-Agent Collaboration
- **Agent Handoffs** - Seamlessly transfer conversations between specialized agents
- **Triage Systems** - Intelligently route queries to the most appropriate agent
- **Orchestration Patterns** - Sequential, parallel, and hierarchical agent coordination
- **Dynamic Routing** - Agents decide when to delegate to other agents

### 🔧 Advanced Tool System
- **Automatic Tool Calling** - Tools are automatically detected and executed
- **Built-in Tools** - File operations, web scraping, system commands, calculations
- **Custom Tools** - Easy decorator-based tool creation
- **Tool Collections** - Organize and manage tool sets
- **Type-Safe** - Full type hints and validation

### 🌐 Web Search (No API Keys!)
- **DuckDuckGo Integration** - Built-in web search with Playwright
- **Search Tools** - Ready-to-use web search capabilities
- **Custom Search Agents** - Create specialized web search agents
- **Real-time Information** - Get up-to-date information from the web

### 📚 Memory & Persistence
- **Multiple Backends** - SQLite, Redis, PostgreSQL, Qdrant, JSON, In-Memory
- **Conversation Memory** - Maintain context across sessions
- **Vector Store Integration** - Qdrant support for semantic search
- **Automatic Context Management** - Smart truncation and summarization
- **Session Management** - Persistent conversations

### 📊 Monitoring & Observability
- **Comprehensive Logging** - Disabled by default, enable when needed
- **Rich Console Output** - Beautiful terminal output with Rich library
- **Performance Tracking** - Track tokens, latency, and costs
- **Statistics & Analytics** - Detailed usage metrics per agent
- **Debugging Support** - Verbose logging modes for development

### 🎯 Thinking Modes (Optional)
- **Chain-of-Thought** - Optional reasoning for supported models
- **Configurable Levels** - None (default), Low, Medium, High
- **Model-Specific** - Only enabled when explicitly configured
- **Performance Tuning** - Adjust reasoning depth as needed

### ⚡ Performance Features
- **Caching** - Response caching for repeated queries
- **Retry Logic** - Configurable retry with exponential backoff
- **Connection Pooling** - Efficient connection management
- **Request Batching** - Batch multiple requests for efficiency
- **Async Support** - Full async/await support for concurrent operations

---

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install ollama-agents-sdk

# With web search support (recommended)
pip install ollama-agents-sdk playwright
playwright install chromium

# With all features including Qdrant vector store
pip install ollama-agents-sdk playwright qdrant-client
```

### Prerequisites

1. **Install Ollama**: [https://ollama.ai](https://ollama.ai)
2. **Pull a model**: `ollama pull qwen2.5-coder:3b-instruct-q8_0`

### Your First Agent

```python
from ollama_agents import Agent, tool

# Define a custom tool
@tool("Get the weather for a city")
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"The weather in {city} is sunny, 72°F"

# Create an agent
agent = Agent(
    name="assistant",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are a helpful assistant. Use tools when needed.",
    tools=[get_weather]
)

# Chat with the agent
response = agent.chat("What's the weather in San Francisco?")
print(response['content'])
```

---

## 📖 Complete Usage Guide

### 1. Creating Agents

```python
from ollama_agents import Agent

agent = Agent(
    name="my_agent",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="Your agent's system prompt here",
    tools=[],  # Optional: list of tool functions
    temperature=0.7,  # Direct parameter
    max_tokens=1000,
    timeout=60
)
```

**Recommended Models:**
- `qwen2.5-coder:3b-instruct-q8_0` - Fast, efficient (default)
- `mistral` - Balanced performance
- `deepseek-coder` - Code-focused
- `llama3.2` - General purpose
- Any other Ollama model

### 2. Tool Calling

Tools are Python functions that agents call automatically:

```python
from ollama_agents import Agent, tool

@tool("Calculate sum of two numbers")
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

@tool("Search for information")
def search(query: str) -> str:
    """Search for information."""
    # Your search implementation
    return f"Results for: {query}"

agent = Agent(
    name="assistant",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are a helpful assistant with access to tools.",
    tools=[add, search]
)

response = agent.chat("What is 15 plus 27?")
print(response['content'])  # Agent will use add tool
```

### 3. Multi-Agent Collaboration

Create specialized agents that work together:

```python
from ollama_agents import Agent, tool

# Create specialized agents
file_agent = Agent(
    name="file_expert",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are a file search expert. Search documents.",
    tools=[search_files]  # Your file search tools
)

web_agent = Agent(
    name="web_expert",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are a web search expert. Search the internet.",
    tools=[web_search]  # Your web search tools
)

# Create triage agent to coordinate
@tool("Route to file search")
def route_to_files(query: str) -> str:
    response = file_agent.chat(query)
    return response['content']

@tool("Route to web search")
def route_to_web(query: str) -> str:
    response = web_agent.chat(query)
    return response['content']

triage = Agent(
    name="coordinator",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="""Route queries to the right agent:
    - Use file search for internal docs
    - Use web search for current events""",
    tools=[route_to_files, route_to_web]
)

# Now ask questions
response = triage.chat("Find our company policy on vacation")
```

### 4. Web Search Integration

Built-in DuckDuckGo search (no API keys!):

```python
from ollama_agents import Agent, tool
from ollama_agents.ddg_search import search_duckduckgo_sync
import json

@tool("Search the web")
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web using DuckDuckGo."""
    results = search_duckduckgo_sync(query, max_results)
    return results

agent = Agent(
    name="web_assistant",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are a web search assistant. Search and summarize.",
    tools=[web_search]
)

response = agent.chat("What are the latest AI developments?")
print(response['content'])
```

### 5. Memory & Persistence

Store and retrieve conversation history:

```python
from ollama_agents import Agent
from ollama_agents.memory import MemoryManager, SQLiteStore

# Create memory store
memory_store = SQLiteStore("conversations.db")
memory_manager = MemoryManager(memory_store)

# Create agent with memory
agent = Agent(
    name="assistant",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are a helpful assistant.",
    enable_memory=True,
    memory_store=memory_store
)

# Conversations are automatically saved
agent.chat("My name is Alice")
agent.chat("What's my name?")  # Agent remembers!
```

### 6. Logging & Debugging

Logging is **OFF by default** for production. Enable when needed:

```python
from ollama_agents import (
    Agent, enable_logging, set_global_log_level, 
    LogLevel, TraceLevel, set_global_tracing_level, enable_stats
)

# Enable logging (only during development/debugging)
enable_logging()
set_global_log_level(LogLevel.DEBUG)  # DEBUG, INFO, WARNING, ERROR
set_global_tracing_level(TraceLevel.VERBOSE)  # OFF, STANDARD, VERBOSE
enable_stats()  # Track performance statistics

# Create agent (logging will now show activity)
agent = Agent(
    name="assistant",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are helpful.",
    enable_tracing=True,  # Enable per-agent tracing
    trace_level=TraceLevel.VERBOSE
)

# All agent actions will be logged
response = agent.chat("Hello!")

# Get statistics
from ollama_agents import get_stats_tracker
stats = get_stats_tracker()
agent_stats = stats.get_agent_stats("assistant")
print(agent_stats)
```

### 7. Thinking Modes (Optional)

Only use with models that support reasoning:

```python
from ollama_agents import Agent, ThinkingMode

# Thinking is OFF by default
agent = Agent(
    name="reasoner",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are a logical reasoning assistant.",
    thinking_mode=None  # Default: No thinking
)

# Enable thinking for complex reasoning tasks
reasoning_agent = Agent(
    name="deep_thinker",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="Think deeply about problems.",
    thinking_mode=ThinkingMode.MEDIUM  # LOW, MEDIUM, HIGH
)
```

### 8. Advanced Configuration

```python
from ollama_agents import Agent, ModelSettings, RetryConfig

agent = Agent(
    name="advanced_agent",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="Advanced agent configuration",
    
    # Generation parameters (direct)
    temperature=0.7,
    top_p=0.9,
    max_tokens=2000,
    
    # Performance features
    enable_cache=True,  # Cache responses
    enable_retry=True,  # Retry on failures
    retry_config=RetryConfig(max_attempts=3),
    
    # Context management
    max_context_length=20000,
    
    # Timeouts
    timeout=120,
    keep_alive="5m",
    
    # Ollama-specific
    host="http://localhost:11434",
    options={"num_gpu": 1}  # Advanced Ollama options
)
```

---

## 🎯 Examples

Check out the `/examples` directory for complete working examples:

1. **`simple_collaborative_agents_example.py`** - Three agents working together (file search, web search, triage)
2. **`basic_examples.py`** - Simple agent creation and tool usage
3. **`web_search_examples.py`** - Web search integration
4. **`orchestration_examples.py`** - Advanced agent orchestration patterns
5. **`performance_examples.py`** - Caching, retry, and optimization

### Running Examples

```bash
# Simple collaborative example (recommended to start)
python examples/simple_collaborative_agents_example.py

# Enable logging to see what's happening
# Edit the example file and uncomment the logging lines at the top

# Other examples
python examples/basic_examples.py
python examples/web_search_examples.py
```

---

## 🏗️ Architecture

### Core Components

1. **Agent** - Main agent class with tool calling and memory
2. **ToolRegistry** - Manages and executes tools
3. **MemoryManager** - Handles conversation persistence
4. **Logger** - Rich console logging (disabled by default)
5. **StatsTracker** - Performance monitoring
6. **ThinkingManager** - Optional reasoning modes

### Agent Lifecycle

```
User Query → Agent → 
  ├─ Load Memory
  ├─ Process Instructions
  ├─ Tool Calling (if needed)
  │   ├─ Execute Tools
  │   └─ Process Results
  ├─ Generate Response
  ├─ Save Memory
  └─ Return Response
```

---

## 🔧 Configuration Options

### Agent Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | Required | Agent identifier |
| `model` | str | `qwen2.5-coder:3b-instruct-q8_0` | Ollama model name |
| `instructions` | str | None | System prompt |
| `tools` | List | [] | Tool functions |
| `temperature` | float | 0.7 | Randomness (0-1) |
| `max_tokens` | int | None | Max response tokens |
| `thinking_mode` | ThinkingMode | None | Reasoning mode (OFF by default) |
| `enable_tracing` | bool | False | Enable tracing |
| `enable_cache` | bool | False | Enable caching |
| `enable_memory` | bool | False | Enable memory |
| `timeout` | int | 30 | Request timeout (seconds) |

### Logging Levels

- **LogLevel.DEBUG** - All details (development)
- **LogLevel.INFO** - Important events (default when enabled)
- **LogLevel.WARNING** - Warnings only
- **LogLevel.ERROR** - Errors only
- **LogLevel.CRITICAL** - Critical issues only

**Default**: Logging is OFF for production performance.

### Tracing Levels

- **TraceLevel.OFF** - No tracing (default)
- **TraceLevel.STANDARD** - Basic tracing
- **TraceLevel.VERBOSE** - Detailed tracing

---

## 🚦 Best Practices

### 1. Keep Logging OFF in Production
```python
# ❌ Don't do this in production
enable_logging()
set_global_log_level(LogLevel.DEBUG)

# ✅ Only enable during development
# enable_logging()  # Comment out for production
```

### 2. Use Specific Models
```python
# ✅ Good - specify exact model
agent = Agent(
    name="assistant",
    model="qwen2.5-coder:3b-instruct-q8_0"
)
```

### 3. Set Thinking Mode Explicitly
```python
# ✅ Good - thinking OFF by default
agent = Agent(name="assistant", model="qwen2.5-coder:3b-instruct-q8_0")

# ✅ Good - explicitly enable when needed
reasoning_agent = Agent(
    name="reasoner",
    model="qwen2.5-coder:3b-instruct-q8_0",
    thinking_mode=ThinkingMode.MEDIUM
)
```

### 4. Use Direct Parameters
```python
# ✅ Good - direct parameters
agent = Agent(
    name="assistant",
    model="qwen2.5-coder:3b-instruct-q8_0",
    temperature=0.7,
    max_tokens=1000
)
```

### 5. Handle Tool Errors
```python
@tool("Search database")
def search_db(query: str) -> str:
    try:
        # Your search logic
        return results
    except Exception as e:
        return json.dumps({"error": str(e)})
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [Ollama](https://ollama.ai) for local LLM inference
- Uses [Rich](https://rich.readthedocs.io/) for beautiful console output
- Inspired by OpenAI's agents pattern
- DuckDuckGo search integration via Playwright

---

## 📞 Support

- **GitHub**: [https://github.com/SlyWolf1/ollama-agent](https://github.com/SlyWolf1/ollama-agent)
- **Issues**: [https://github.com/SlyWolf1/ollama-agent/issues](https://github.com/SlyWolf1/ollama-agent/issues)
- **Email**: brianmanda44@gmail.com

---

## 🗺️ Roadmap

- [ ] More memory backends (MongoDB, Pinecone)
- [ ] Advanced agent orchestration patterns
- [ ] Web UI for agent management
- [ ] More built-in tools
- [ ] Performance optimizations
- [ ] Agent templates and presets
- [ ] Multi-modal support (images, audio)
- [ ] Agent marketplace

---

**Built with ❤️ for the Ollama community**
