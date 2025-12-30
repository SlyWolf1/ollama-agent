# Ollama Agents SDK

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Advanced agent framework for Ollama with multi-agent collaboration, tool calling, web search, and more.**

Build intelligent AI agents that can collaborate, use tools, search the web, and manage complex workflows - all powered by local Ollama models.

## ✨ Features

- 🤝 **Multi-Agent Collaboration** - Coordinate multiple specialized agents
- 🔧 **Tool Calling** - Automatic tool detection and execution
- 🌐 **Web Search** - DuckDuckGo integration (no API keys!)
- 📚 **Vector Store** - Qdrant integration for document search
- 💾 **Memory** - SQLite and Qdrant memory backends
- 📊 **Statistics** - Track agent performance and usage
- 🔀 **Agent Handoffs** - Transfer queries between agents
- 📝 **Logging & Tracing** - Comprehensive debugging support
- 🎯 **Thinking Modes** - Optional chain-of-thought reasoning

## 🚀 Quick Start

### Installation

```bash
pip install ollama-agents-sdk
```

**For web search functionality:**
```bash
pip install playwright
playwright install chromium
```

### Basic Agent

```python
from ollama_agents import Agent, tool

# Define a custom tool
@tool("Get the weather")
def get_weather(city: str) -> str:
    """Get weather for a city"""
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

## 📖 Usage Guide

### 1. Creating Agents

```python
from ollama_agents import Agent, ModelSettings

agent = Agent(
    name="my_agent",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="Your agent's system prompt here",
    tools=[],  # Optional: list of tool functions
    settings=ModelSettings(
        temperature=0.7,
        max_tokens=1000
    ),
    timeout=60
)
```

### 2. Using Tools

Tools are automatically called when needed:

```python
from ollama_agents import Agent, tool

@tool("Calculate sum")
def add(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

@tool("Calculate product")
def multiply(a: int, b: int) -> int:
    """Multiply two numbers together"""
    return a * b

agent = Agent(
    name="calculator",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are a calculator. Use the provided tools to perform calculations.",
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

## 🗺️ Roadmap

- [ ] More memory backends
- [ ] Advanced agent orchestration patterns
- [ ] Web UI for agent management
- [ ] More built-in tools
- [ ] Performance optimizations

## 📈 Version History

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

---

**Made with ❤️ for the Ollama community**
