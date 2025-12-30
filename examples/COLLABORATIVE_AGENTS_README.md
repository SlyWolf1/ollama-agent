# Collaborative Multi-Agent System Example

This example demonstrates how to build a sophisticated multi-agent system where three specialized agents work together to handle different types of queries.

## Architecture

The system consists of three specialized agents:

### 1. **File Search Agent** 🗂️
- **Purpose**: Searches documents stored in Qdrant vector database
- **Collection**: `vector_store`
- **Model**: `qwen2.5-coder:3b-instruct-q8_0`
- **Tools**:
  - `search_vector_store()` - Search documents by query
  - `get_document_by_id()` - Retrieve specific documents
  - `list_collections()` - List available collections

### 2. **Web Search Agent** 🌐
- **Purpose**: Searches the internet for current information
- **Provider**: Brave Search API
- **Model**: `llama3.2`
- **Capabilities**: Real-time data, news, weather, current events

### 3. **Triage Agent** 🎯
- **Purpose**: Coordinates and routes queries to appropriate agents
- **Model**: `qwen2.5-coder:3b-instruct-q8_0`
- **Intelligence**: Uses HIGH thinking mode for decision making
- **Tools**:
  - `route_to_file_search()` - Send queries to file search agent
  - `route_to_web_search()` - Send queries to web search agent

## How It Works

```
User Query
    ↓
Triage Agent (Analyzes & Routes)
    ↓
    ├─→ File Search Agent (Static Documents) → Qdrant Vector Store
    │
    └─→ Web Search Agent (Current Info) → Internet Search
```

The triage agent intelligently determines which specialized agent should handle each query:

- **Static/Historical Queries** → File Search Agent
- **Current/Real-time Queries** → Web Search Agent  
- **Hybrid Queries** → Both agents (synthesizes responses)

## Prerequisites

### 1. Qdrant Vector Database

Install and run Qdrant:

```bash
# Using Docker (recommended)
docker run -p 6333:6333 qdrant/qdrant

# Or using Docker Compose
docker-compose up -d
```

Install the Python client:
```bash
pip install qdrant-client
```

### 2. Create Vector Store Collection

```python
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

client = QdrantClient(host="localhost", port=6333)

# Create collection
client.create_collection(
    collection_name="vector_store",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

# Add your documents
# (See Qdrant documentation for embedding and uploading documents)
```

### 3. Brave Search API Key (Optional)

For web search functionality:

1. Visit: https://brave.com/search/api/
2. Sign up (free tier: 2,000 queries/month)
3. Copy your API key

## Usage

### Basic Usage

```python
from examples.collaborative_agents_example import (
    create_file_search_agent,
    create_web_search_agent,
    create_triage_agent
)

# Create agents
file_agent = create_file_search_agent()
web_agent = create_web_search_agent(api_key="YOUR_BRAVE_API_KEY")
triage = create_triage_agent(file_agent, web_agent)

# Use the triage agent
response = triage.chat("Search our docs for API authentication info")
print(response['content'])
```

### Running the Example

```bash
cd /Users/brianmanda/PycharmProjects/library
python3 examples/collaborative_agents_example.py
```

### Interactive Mode

Uncomment the interactive section at the end of the file to enable:

```python
while True:
    user_query = input("\n🤔 Your query: ").strip()
    if user_query.lower() in ['exit', 'quit']:
        break
    response = triage_agent.chat(user_query)
    print(f"\n🤖 Response:\n{response['content']}")
```

## Example Queries

### File Search Queries
```python
# Search internal documents
"Search our document store for information about API authentication"
"Find documents related to security policies"
"What does our style guide say about Python formatting?"
```

### Web Search Queries
```python
# Current information
"What are the latest developments in AI this week?"
"Current weather in San Francisco"
"Latest tech news today"
```

### Hybrid Queries
```python
# Requires both agents
"Compare our internal security policies with current industry best practices"
"How do our API docs compare to modern REST API standards?"
```

## Key Features

### 1. **Intelligent Routing**
The triage agent analyzes queries and routes them to the appropriate specialist:

```python
if "current" in query or "latest" in query:
    # Route to web search agent
elif "our docs" in query or "internal" in query:
    # Route to file search agent
```

### 2. **Multi-Source Synthesis**
For complex queries, the triage agent can consult both agents and combine their responses.

### 3. **Tool-Based Architecture**
Each agent uses the `@tool` decorator to expose its capabilities:

```python
@tool("Search documents in Qdrant vector store")
def search_vector_store(query: str, limit: int = 5) -> str:
    # Implementation
    pass
```

### 4. **Error Handling**
Graceful fallbacks when Qdrant is unavailable or API keys are missing.

### 5. **Thinking Modes**
Different agents use appropriate thinking modes:
- File Search: MEDIUM (balanced reasoning)
- Web Search: MEDIUM (balanced reasoning)
- Triage: HIGH (deep decision making)

## Configuration

### Qdrant Connection

Modify connection settings in the tool functions:

```python
client = QdrantClient(
    host="localhost",  # Change if Qdrant is remote
    port=6333,         # Default Qdrant port
    # For cloud: url="https://your-instance.cloud.qdrant.io",
    # api_key="your-api-key"
)
```

### Model Selection

Change models per agent:

```python
agent = Agent(
    name="my_agent",
    model="llama3.2",  # or qwen2.5-coder, mistral, etc.
    # ...
)
```

### Search Provider

Switch between search providers:

```python
from ollama_agents import SearchProvider

enable_web_search(
    agent,
    provider=SearchProvider.BRAVE,      # or DUCKDUCKGO, SEARXNG
    api_key="your-key"
)
```

## Testing Individual Agents

Test each agent separately:

```python
# Test file search agent
test_file_search_agent()

# Test web search agent
test_web_search_agent(brave_api_key="YOUR_KEY")
```

## Customization

### Add New Tools

Add specialized tools to any agent:

```python
@tool("Custom tool description")
def my_custom_tool(param: str) -> str:
    """Tool implementation"""
    return result

agent = Agent(
    name="custom_agent",
    tools=[my_custom_tool, other_tool],
    # ...
)
```

### Add More Agents

Extend the triage system with additional specialists:

```python
# Create new specialized agent
database_agent = Agent(
    name="database_agent",
    instructions="You query SQL databases",
    tools=[query_database],
)

# Add routing tool to triage
@tool("Route to database agent")
def route_to_database(query: str) -> str:
    return database_agent.chat(query)['content']

# Update triage agent tools
triage_agent.tools.append(route_to_database)
```

## Troubleshooting

### Qdrant Connection Issues
```
Error: "Failed to connect to Qdrant"
Solution: Ensure Qdrant is running on localhost:6333
```

### Missing Collections
```
Error: "Collection 'vector_store' not found"
Solution: Create the collection before searching
```

### Web Search Not Working
```
Warning: "Web search agent created without API key"
Solution: Provide a valid Brave Search API key
```

### Model Not Found
```
Error: "Model not found"
Solution: Pull the model: ollama pull qwen2.5-coder:3b-instruct-q8_0
```

## Performance Tips

1. **Connection Pooling**: Reuse Qdrant client across queries
2. **Caching**: Enable response caching for repeated queries
3. **Batch Processing**: Process multiple queries in parallel
4. **Context Management**: Clear conversation history periodically

## Advanced Features

### Enable Tracing
```python
agent = Agent(
    name="my_agent",
    enable_tracing=True,
    trace_level=TraceLevel.DEBUG
)
```

### Enable Memory
```python
from ollama_agents import InMemoryStore

agent = Agent(
    name="my_agent",
    enable_memory=True,
    memory_store=InMemoryStore()
)
```

### Enable Caching
```python
from ollama_agents import enable_caching

agent = Agent(name="my_agent", enable_cache=True)
enable_caching(agent)
```

## Related Examples

- `basic_examples.py` - Basic agent usage
- `web_search_examples.py` - Web search capabilities
- `advanced_examples.py` - Multi-agent systems
- `mcp_rich_context_examples.py` - Context management

## Resources

- [Ollama Agents SDK Documentation](../README.md)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Brave Search API](https://brave.com/search/api/)
- [Ollama Models](https://ollama.ai/library)

## License

This example is part of the Ollama Agents SDK project.
