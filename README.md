# Ollama Agents SDK

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/ollama-agents-sdk.svg)](https://badge.fury.io/py/ollama-agents-sdk)

**Production-ready agent framework for Ollama with multi-agent collaboration, tool calling, web search, and advanced memory backends.**

Build intelligent AI agents that can collaborate, use tools, search the web, and manage complex workflows - all powered by local Ollama models. No API keys required!

## ✨ Key Features

### 🤝 Multi-Agent Collaboration
- **Agent Handoffs** - Seamlessly transfer conversations between specialized agents
- **Triage Systems** - Route queries to the most appropriate agent
- **Orchestration Patterns** - Sequential, parallel, and hierarchical agent coordination

### 🔧 Advanced Tool System
- **Automatic Tool Calling** - Tools are automatically detected and executed
- **Built-in Tools** - File operations, web scraping, system commands, and more
- **Custom Tools** - Easy decorator-based tool creation
- **Tool Collections** - Organize and manage tool sets

### 🌐 Web Search (No API Keys!)
- **DuckDuckGo Integration** - Built-in web search with Playwright
- **Search Tools** - Ready-to-use web search capabilities
- **Custom Search Agents** - Create specialized web search agents

### 📚 Memory & Persistence
- **Multiple Backends** - SQLite, Redis, PostgreSQL, Qdrant, JSON, In-Memory
- **Conversation Memory** - Maintain context across sessions
- **Vector Store Integration** - Qdrant support for semantic search
- **Automatic Context Management** - Smart truncation and summarization

### 📊 Monitoring & Observability
- **Comprehensive Logging** - Disabled by default, enable when needed
- **Rich Console Output** - Beautiful terminal output with Rich
- **Performance Tracking** - Track tokens, latency, and costs
- **Statistics & Analytics** - Detailed usage metrics per agent

### 🎯 Thinking Modes (Optional)
- **Chain-of-Thought** - Optional reasoning for supported models
- **Configurable Levels** - None, Low, Medium, High
- **Model-Specific** - Works only with models that support thinking

### ⚡ Performance Features
- **Caching** - Response caching for repeated queries
- **Retry Logic** - Configurable retry with exponential backoff
- **Connection Pooling** - Efficient connection management
- **Request Batching** - Batch multiple requests for efficiency

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install ollama-agents-sdk

# With web search support
pip install ollama-agents-sdk playwright
playwright install chromium

# With all features (Qdrant vector store)
pip install ollama-agents-sdk playwright qdrant-client
```

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

## 📖 Complete Usage Guide

### 1. Creating Agents

```python
from ollama_agents import Agent, ModelSettings

agent = Agent(
    name="my_agent",
    model="qwen2.5-coder:3b-instruct-q8_0",  # Any Ollama model
    instructions="Your agent's system prompt here",
    tools=[],  # Optional: list of tool functions
    settings=ModelSettings(
        temperature=0.7,
        max_tokens=1000
    ),
    timeout=60
)
```

**Available Models:**
- `qwen2.5-coder:3b-instruct-q8_0` - Fast, efficient (recommended)
- `llama3.2` - General purpose
- `mistral` - Balanced performance
- `deepseek-coder` - Code-focused
- Any other Ollama model

### 2. Tool Calling

Tools are Python functions that agents can call automatically:

```python
from ollama_agents import Agent, tool

@tool("Calculate sum of two numbers")
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

@tool("Calculate product of two numbers")
def multiply(a: int, b: int) -> int:
    """Multiply two numbers together."""
    return a * b

agent = Agent(
    name="calculator",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are a calculator. Use the provided tools.",
    tools=[add, multiply]
)

response = agent.chat("What is 15 times 23?")
print(response['content'])  # Agent will use multiply tool
```

### 3. Multi-Agent Collaboration

Create specialized agents that work together:

```python
from ollama_agents import Agent, tool

# Specialized agent 1
@tool("Search documents")
def search_docs(query: str) -> str:
    return f"Found documents about: {query}"

doc_agent = Agent(
    name="doc_search",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You search internal documents.",
    tools=[search_docs]
)

# Specialized agent 2
@tool("Search web")
def search_web(query: str) -> str:
    return f"Web results for: {query}"

web_agent = Agent(
    name="web_search",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You search the web.",
    tools=[search_web]
)

# Coordinator agent
@tool("Route to document search")
def route_to_docs(query: str) -> str:
    response = doc_agent.chat(query)
    return response['content']

@tool("Route to web search")
def route_to_web(query: str) -> str:
    response = web_agent.chat(query)
    return response['content']

coordinator = Agent(
    name="coordinator",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="""You coordinate between document and web search.
    Route internal queries to docs, external queries to web.""",
    tools=[route_to_docs, route_to_web]
)

# Use the coordinator
response = coordinator.chat("Find our company policies")
print(response['content'])
```

### 4. Web Search (Built-in)

Use DuckDuckGo for web search without API keys:

```python
from ollama_agents import Agent, tool
from ollama_agents.ddg_search import search_duckduckgo_sync
import json

@tool("Search the web")
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web using DuckDuckGo."""
    try:
        results = search_duckduckgo_sync(query, max_results)
        return results
    except Exception as e:
        return json.dumps({"error": str(e)})

agent = Agent(
    name="web_searcher",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You search the web and summarize findings.",
    tools=[web_search]
)

response = agent.chat("What are the latest AI developments?")
print(response['content'])
```

### 5. Memory & Persistence

Add memory to agents for context retention:

```python
from ollama_agents import Agent, SQLiteMemoryStore

# Create memory store
memory = SQLiteMemoryStore(db_path="agent_memory.db")

agent = Agent(
    name="assistant",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You remember past conversations.",
    enable_memory=True,
    memory_store=memory
)

# Conversations are automatically saved and retrieved
response1 = agent.chat("My name is John")
response2 = agent.chat("What's my name?")  # Agent remembers!
```

**Available Memory Backends:**
- `InMemoryStore` - Temporary (default)
- `SQLiteMemoryStore` - Local file persistence
- `RedisMemoryStore` - Redis cache
- `PostgresMemoryStore` - PostgreSQL database
- `JSONFileMemoryStore` - Simple JSON files

### 6. Logging & Debugging

Logging is **disabled by default** for performance. Enable when needed:

```python
from ollama_agents import (
    Agent, 
    enable_logging, 
    set_global_log_level, 
    LogLevel,
    enable_stats
)

# Enable detailed logging
enable_logging()
set_global_log_level(LogLevel.DEBUG)  # DEBUG, INFO, WARNING, ERROR
enable_stats()  # Track performance metrics

agent = Agent(
    name="assistant",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are helpful."
)

response = agent.chat("Hello!")
# Logs will show detailed execution flow
```

**Log Levels:**
- `LogLevel.DEBUG` - Verbose details (development)
- `LogLevel.INFO` - Key events (recommended)
- `LogLevel.WARNING` - Warnings only
- `LogLevel.ERROR` - Errors only

### 7. Model Settings

Fine-tune model behavior:

```python
from ollama_agents import Agent, ModelSettings

agent = Agent(
    name="creative_writer",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are a creative writer.",
    settings=ModelSettings(
        temperature=0.9,      # Creativity (0.0-1.0)
        top_p=0.9,           # Nucleus sampling
        max_tokens=2000,     # Max response length
        frequency_penalty=0.5,
        presence_penalty=0.5,
        # Note: thinking_mode only works with supported models
        # thinking_mode=ThinkingMode.MEDIUM  # Optional
    )
)
```

### 8. Performance Optimization

```python
from ollama_agents import Agent, enable_caching, enable_connection_pooling

# Enable caching for repeated queries
enable_caching()

# Enable connection pooling
enable_connection_pooling()

agent = Agent(
    name="efficient_agent",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are efficient.",
    enable_cache=True,
    enable_retry=True  # Auto-retry on failures
)
```

## 🎯 Complete Examples

### Example 1: Collaborative Agents

See `examples/simple_collaborative_agents.py` for a complete example with:
- File search agent (Qdrant)
- Web search agent (DuckDuckGo)
- Triage coordinator agent

### Example 2: Tool-Heavy Agent

```python
from ollama_agents import Agent, tool
import os
import subprocess

@tool("List files in directory")
def list_files(directory: str = ".") -> str:
    """List all files in a directory."""
    try:
        files = os.listdir(directory)
        return "\n".join(files)
    except Exception as e:
        return f"Error: {str(e)}"

@tool("Read file contents")
def read_file(filepath: str) -> str:
    """Read contents of a file."""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}"

@tool("Execute shell command")
def run_command(command: str) -> str:
    """Execute a shell command safely."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=5
        )
        return result.stdout or result.stderr
    except Exception as e:
        return f"Error: {str(e)}"

agent = Agent(
    name="system_assistant",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You help with file and system operations. Use tools carefully.",
    tools=[list_files, read_file, run_command]
)

response = agent.chat("What files are in the current directory?")
print(response['content'])
```

## 📚 Advanced Features

### Vector Store Integration (Qdrant)

```python
from ollama_agents import Agent, tool
from qdrant_client import QdrantClient
import json

@tool("Search vector database")
def search_vectors(query: str, limit: int = 5) -> str:
    """Search documents in Qdrant vector store."""
    client = QdrantClient(host="localhost", port=6333)
    # Add your embedding logic here
    results = client.search(
        collection_name="my_collection",
        query_vector=[0.0] * 384,  # Your embedding
        limit=limit
    )
    return json.dumps([r.payload for r in results])

agent = Agent(
    name="doc_searcher",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You search documents using vector similarity.",
    tools=[search_vectors]
)
```

### Orchestration Patterns

```python
from ollama_agents import AgentOrchestrator, OrchestrationPattern

orchestrator = AgentOrchestrator()

# Sequential execution
result = orchestrator.orchestrate(
    agents=[agent1, agent2, agent3],
    task="Analyze this data",
    pattern=OrchestrationPattern.SEQUENTIAL
)

# Parallel execution
result = orchestrator.orchestrate(
    agents=[agent1, agent2, agent3],
    task="Generate ideas",
    pattern=OrchestrationPattern.PARALLEL
)
```

## 🛠️ Configuration

### Environment Variables

```bash
# Ollama host (default: http://localhost:11434)
export OLLAMA_HOST=http://localhost:11434

# Enable debug logging
export OLLAMA_AGENTS_DEBUG=1

# Cache directory
export OLLAMA_AGENTS_CACHE_DIR=~/.ollama_agents_cache
```

### Model Configuration

```python
from ollama_agents import Agent, ModelSettings

# Precise mode (low temperature, deterministic)
precise_agent = Agent(
    name="precise",
    model="qwen2.5-coder:3b-instruct-q8_0",
    settings=ModelSettings(temperature=0.1, top_p=0.1)
)

# Creative mode (high temperature, varied)
creative_agent = Agent(
    name="creative",
    model="qwen2.5-coder:3b-instruct-q8_0",
    settings=ModelSettings(temperature=0.9, top_p=0.9)
)

# Balanced mode (default)
balanced_agent = Agent(
    name="balanced",
    model="qwen2.5-coder:3b-instruct-q8_0",
    settings=ModelSettings(temperature=0.7, top_p=0.9)
)
```

## 📝 Best Practices

### 1. Logging
- **Disable by default** - Logging is off for performance
- **Enable for debugging** - Use `enable_logging()` when developing
- **Use appropriate levels** - INFO for production, DEBUG for development

### 2. Model Selection
- **Fast tasks** - `qwen2.5-coder:3b-instruct-q8_0` (3B parameters)
- **Complex reasoning** - Larger models like `llama3.2:70b`
- **Code generation** - `deepseek-coder`, `codellama`

### 3. Tool Design
- **Clear descriptions** - Tools need good docstrings
- **Type hints** - Use Python type hints for parameters
- **Error handling** - Return error messages, don't raise exceptions

### 4. Agent Instructions
- **Be specific** - Clear, detailed instructions work best
- **Include examples** - Show how to use tools
- **Set expectations** - Define the agent's role clearly

### 5. Performance
- **Enable caching** - For repeated queries
- **Use connection pooling** - For high-throughput applications
- **Batch requests** - When possible

## 🔧 Troubleshooting

### Issue: Agent doesn't call tools
- Ensure tool descriptions are clear
- Check model supports tool calling
- Verify instructions mention tools

### Issue: Slow performance
- Enable caching: `enable_caching()`
- Use smaller models for simple tasks
- Enable connection pooling

### Issue: Memory usage high
- Disable logging in production
- Use context truncation
- Clear conversation history periodically

### Issue: Qdrant connection failed
```bash
# Start Qdrant with Docker
docker run -p 6333:6333 qdrant/qdrant
```

### Issue: Web search not working
```bash
# Install Playwright browsers
pip install playwright
playwright install chromium
```

## 📦 What's Included

- **Core** - Agent, tool system, handoffs
- **Tools** - Built-in tools for common tasks
- **Memory** - Multiple backend options
- **Search** - DuckDuckGo integration
- **Logging** - Rich console output
- **Stats** - Performance tracking
- **Caching** - Response caching
- **Retry** - Automatic retry logic
- **Orchestration** - Multi-agent patterns
- **Web UI** - Visual agent management (experimental)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🔗 Links

- **GitHub**: https://github.com/SlyWolf1/ollama-agent
- **PyPI**: https://pypi.org/project/ollama-agents-sdk/
- **Issues**: https://github.com/SlyWolf1/ollama-agent/issues
- **Ollama**: https://ollama.ai

## 📧 Support

- **Email**: brianmanda44@gmail.com
- **GitHub Issues**: https://github.com/SlyWolf1/ollama-agent/issues

## ⭐ Star History

If you find this project useful, please consider giving it a star on GitHub!

---

**Made with ❤️ for the Ollama community**
    tools=[add, multiply]
)

response = agent.chat("What is 25 + 17?")
print(response['content'])  # Agent will use the add tool

response = agent.chat("What is 8 times 9?")
print(response['content'])  # Agent will use the multiply tool
```

### 3. Web Search with DuckDuckGo

```python
from ollama_agents import Agent, tool
from ollama_agents.ddg_search import search_duckduckgo_sync

@tool("Search the web")
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web using DuckDuckGo"""
    return search_duckduckgo_sync(query, max_results)

agent = Agent(
    name="web_assistant",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are a research assistant. Use web_search to find current information.",
    tools=[web_search]
)

response = agent.chat("What are the latest developments in AI?")
print(response['content'])
```

### 4. Multi-Agent Collaboration

Create specialized agents that work together:

```python
from ollama_agents import Agent, tool

# Create specialized agents
researcher = Agent(
    name="researcher",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You research topics thoroughly and provide detailed information.",
    tools=[web_search]
)

writer = Agent(
    name="writer",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You write clear, engaging content based on research provided."
)

# Create coordinator agent
@tool("Get research")
def get_research(topic: str) -> str:
    """Get research on a topic"""
    response = researcher.chat(f"Research this topic: {topic}")
    return response['content']

@tool("Write article")
def write_article(research: str, style: str) -> str:
    """Write an article based on research"""
    response = writer.chat(f"Write a {style} article based on: {research}")
    return response['content']

coordinator = Agent(
    name="coordinator",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="""You coordinate research and writing.
    First use get_research to gather information, then use write_article to create content.""",
    tools=[get_research, write_article]
)

# Use the multi-agent system
response = coordinator.chat("Create a blog post about quantum computing")
print(response['content'])
```

### 5. Vector Store (Qdrant) Integration

```python
from ollama_agents import Agent, tool
from qdrant_client import QdrantClient

# Setup Qdrant client
client = QdrantClient(host="localhost", port=6333)

@tool("Search documents")
def search_docs(query: str, limit: int = 5) -> str:
    """Search the document database"""
    # Generate embedding for query (simplified)
    results = client.search(
        collection_name="my_docs",
        query_vector=[0.0] * 384,  # Replace with actual embedding
        limit=limit
    )
    return str([r.payload for r in results])

agent = Agent(
    name="doc_assistant",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You help users find information in documents. Use search_docs tool.",
    tools=[search_docs]
)

response = agent.chat("Find information about project timelines")
print(response['content'])
```

### 6. Agent Memory

```python
from ollama_agents import Agent
from ollama_agents.memory import SQLiteMemory

# Create agent with memory
agent = Agent(
    name="assistant_with_memory",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You remember past conversations.",
    memory=SQLiteMemory("agent_memory.db")
)

# Conversation is remembered across chats
agent.chat("My name is Alice")
agent.chat("What's my name?")  # Agent will remember "Alice"
```

### 7. Statistics and Monitoring

```python
from ollama_agents import Agent, enable_stats, get_stats

# Enable statistics tracking
enable_stats()

agent = Agent(
    name="monitored_agent",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are a helpful assistant."
)

# Use the agent
agent.chat("Hello!")
agent.chat("Tell me about Python")

# Get statistics
stats = get_stats()
print(f"Total API calls: {stats.api_calls}")
print(f"Tokens used: {stats.total_tokens}")
print(f"Tools called: {stats.tools_called}")
```

### 8. Logging and Debugging

```python
from ollama_agents import Agent, LogLevel, set_global_log_level

# Set log level
set_global_log_level(LogLevel.DEBUG)  # DEBUG, INFO, WARNING, ERROR

agent = Agent(
    name="debug_agent",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are a helpful assistant.",
    enable_tracing=True  # Enable detailed tracing
)

# Detailed logs will be printed
agent.chat("Hello!")
```

## 🎯 Complete Example: Collaborative Agents

Here's a complete example with three agents working together:

```python
from ollama_agents import Agent, tool, ModelSettings
from ollama_agents.ddg_search import search_duckduckgo_sync

# 1. File Search Agent (searches local documents)
@tool("Search documents")
def search_documents(query: str) -> str:
    """Search local document database"""
    # Your document search logic here
    return f"Found documents about: {query}"

file_agent = Agent(
    name="file_search_agent",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You search local documents and provide relevant information.",
    tools=[search_documents]
)

# 2. Web Search Agent (searches the internet)
@tool("Web search")
def web_search(query: str) -> str:
    """Search the web with DuckDuckGo"""
    return search_duckduckgo_sync(query, max_results=5)

web_agent = Agent(
    name="web_search_agent",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You search the web for current information and provide results.",
    tools=[web_search]
)

# 3. Triage Agent (coordinates between file and web search)
@tool("Route to file search")
def route_to_files(query: str) -> str:
    """Route query to file search agent"""
    response = file_agent.chat(query)
    return response['content']

@tool("Route to web search")
def route_to_web(query: str) -> str:
    """Route query to web search agent"""
    response = web_agent.chat(query)
    return response['content']

triage_agent = Agent(
    name="triage_agent",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="""You coordinate between file and web search agents.
    
    For queries about:
    - Stored documents, company info, internal data → use route_to_files
    - Current events, news, web information → use route_to_web
    
    Always show the complete response from the specialized agent.""",
    tools=[route_to_files, route_to_web],
    settings=ModelSettings(temperature=0.2)
)

# Use the system
response = triage_agent.chat("What's the latest news about AI?")
print(response['content'])
```

## 🔧 Configuration Options

### Model Settings

```python
from ollama_agents import ModelSettings, ThinkingMode

settings = ModelSettings(
    temperature=0.7,        # Creativity (0.0 - 1.0)
    max_tokens=2000,        # Maximum response length
    top_p=0.9,              # Nucleus sampling
    top_k=40,               # Top-k sampling
    thinking_mode=None      # Optional: ThinkingMode.MEDIUM for reasoning
)
```

### Agent Parameters

```python
agent = Agent(
    name="agent_name",              # Agent identifier
    model="model_name",             # Ollama model to use
    instructions="system_prompt",   # Agent behavior
    tools=[],                       # List of tool functions
    settings=ModelSettings(...),    # Model settings
    memory=None,                    # Optional memory backend
    timeout=60,                     # Request timeout in seconds
    enable_tracing=False,           # Enable detailed logging
    stream=False                    # Stream responses
)
```

## 📚 Examples

Check the `examples/` directory for complete examples:

- `collaborative_agents_example.py` - Multi-agent system with triage
- `example_memory.py` - Memory usage examples
- `example_memory_backends.py` - Different memory backends

Run an example:
```bash
python examples/collaborative_agents_example.py
```

## 🧪 Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run specific test
pytest tests/test_basic.py -v

# Run with coverage
pytest tests/ --cov=ollama_agents --cov-report=term-missing
```

## 📦 Dependencies

- `ollama>=0.6.1` - Ollama Python client
- `rich>=13.0.0` - Terminal output formatting
- `qdrant-client>=1.0.0` - Vector database (optional)
- `playwright>=1.40.0` - Web scraping for search (optional)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on top of [Ollama](https://ollama.ai/)
- Inspired by multi-agent frameworks and tool-calling patterns

## 📞 Support

- GitHub Issues: [Report a bug](https://github.com/SlyWolf1/ollama-agent/issues)
- Documentation: [Full docs](https://github.com/SlyWolf1/ollama-agent#readme)
- Email: brianmanda44@gmail.com

## 🎉 New in v0.2.0

### ✅ More Memory Backends
- MongoDB memory store
- JSON file memory store (portable)
- Existing: SQLite, Redis, PostgreSQL, Qdrant

### ✅ Advanced Orchestration Patterns
- **Sequential**: Pass output from one agent to the next
- **Parallel**: Run agents simultaneously and aggregate results
- **Hierarchical**: Coordinator delegates to worker agents
- **Consensus**: Agents vote to reach agreement
- **Debate**: Agents argue to find best answer
- **Pipeline**: Chain agents with transformations

### ✅ Web UI for Agent Management
- Beautiful web interface at `http://localhost:5000`
- Chat with multiple agents
- Switch between agents
- View conversation history
- Monitor statistics

### ✅ Built-in Tools
- **File Tools**: read_file, write_file, list_directory
- **Web Tools**: http_get, http_post
- **System Tools**: execute_command, get_current_time, get_env_var
- **Data Tools**: parse_json, format_json, calculate
- **Text Tools**: count_words, count_characters, to_uppercase, to_lowercase

### ✅ Performance Optimizations
- LRU cache with size limits
- Request batching
- Connection pooling
- Response caching with TTL
- Memory-efficient caching

## 📈 Version History

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

---

**Made with ❤️ for the Ollama community**

### 9. Built-in Tools

Use ready-made tools for common tasks:

```python
from ollama_agents import Agent, get_tool_collection

# Get all file tools
file_agent = Agent(
    name="file_assistant",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="Help with file operations",
    tools=get_tool_collection("file")  # read_file, write_file, list_directory
)

# Get all text tools
text_agent = Agent(
    name="text_processor",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="Process text",
    tools=get_tool_collection("text")  # count_words, to_uppercase, etc
)

# Get ALL built-in tools
multi_agent = Agent(
    name="multi_agent",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="Versatile assistant",
    tools=get_tool_collection("all")
)
```

Available collections: `"file"`, `"web"`, `"system"`, `"data"`, `"text"`, `"all"`

### 10. Advanced Orchestration

Coordinate multiple agents with various patterns:

```python
from ollama_agents import Agent, orchestrate, OrchestrationPattern, AgentOrchestrator

researcher = Agent(name="researcher", model="qwen2.5-coder:3b-instruct-q8_0", instructions="Research topics")
analyst = Agent(name="analyst", model="qwen2.5-coder:3b-instruct-q8_0", instructions="Analyze information")
writer = Agent(name="writer", model="qwen2.5-coder:3b-instruct-q8_0", instructions="Write content")

# Sequential: researcher → analyst → writer
result = orchestrate(
    agents=[researcher, analyst, writer],
    query="Explain quantum computing",
    pattern=OrchestrationPattern.SEQUENTIAL
)

# Parallel: all agents run simultaneously
result = orchestrate(
    agents=[researcher, analyst, writer],
    query="What is AI?",
    pattern=OrchestrationPattern.PARALLEL
)

# Debate: agents argue to find best answer
orchestrator = AgentOrchestrator([agent1, agent2])
result = orchestrator.debate(
    query="Should we adopt AI?",
    rounds=2
)

# Consensus: agents vote
result = orchestrator.consensus(
    query="What is 2+2?",
    threshold=0.6
)
```

### 11. Web UI

Launch a web interface to manage agents:

```python
from ollama_agents import Agent, AgentManager, create_web_ui, get_tool_collection

# Create manager
manager = AgentManager()

# Add agents
assistant = Agent(name="assistant", model="qwen2.5-coder:3b-instruct-q8_0", instructions="General assistant")
coder = Agent(name="coder", model="qwen2.5-coder:3b-instruct-q8_0", instructions="Coding help", tools=get_tool_collection("data"))

manager.add_agent(assistant)
manager.add_agent(coder)

# Start web UI
create_web_ui(manager, host="0.0.0.0", port=5000)
# Open http://localhost:5000 in your browser
```

**Web UI Features:**
- 💬 Chat with multiple agents
- 🔄 Switch between agents seamlessly
- 📜 View full conversation history
- 📊 Monitor agent statistics
- 🎨 Beautiful, responsive interface

### 12. Performance Optimization

Enable caching and performance features:

```python
from ollama_agents import Agent
from ollama_agents.performance import enable_response_caching, LRUCache

# Enable response caching (saves duplicate API calls)
enable_response_caching(max_size=1000, ttl_seconds=3600)

agent = Agent(name="assistant", model="qwen2.5-coder:3b-instruct-q8_0", instructions="Helper")

# First call - hits API
response1 = agent.chat("What is Python?")

# Second call - uses cache!
response2 = agent.chat("What is Python?")

# Use LRU cache for custom data
cache = LRUCache(max_size=100, max_memory_mb=10)
cache.set("key", "value")
value = cache.get("key")
```

### 13. More Memory Backends

Choose from multiple memory storage options:

```python
from ollama_agents import Agent
from ollama_agents.memory import (
    SQLiteMemoryStore,
    RedisMemoryStore,
    PostgresMemoryStore,
    MongoDBMemoryStore,
    JSONFileMemoryStore
)

# SQLite (file-based, portable)
memory = SQLiteMemoryStore("agent_memory.db")

# Redis (fast, in-memory)
memory = RedisMemoryStore(host="localhost", port=6379)

# PostgreSQL (robust, scalable)
memory = PostgresMemoryStore(
    host="localhost",
    database="agents",
    user="user",
    password="pass"
)

# MongoDB (flexible, document-based)
memory = MongoDBMemoryStore(
    connection_string="mongodb://localhost:27017/",
    database="agents"
)

# JSON File (simple, human-readable)
memory = JSONFileMemoryStore("memory.json")

# Use with agent
agent = Agent(
    name="assistant",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You remember conversations",
    memory=memory
)
```

