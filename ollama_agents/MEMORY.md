# Ollama Agents Memory System

The Ollama Agents memory system provides persistent and temporary memory storage for AI agents, allowing them to remember information across conversations and sessions.

## Memory Backends

The memory system supports multiple storage backends:

- **SQLite**: Persistent storage using SQLite database files
- **Redis**: High-performance in-memory storage with optional persistence
- **PostgreSQL**: Robust enterprise-grade persistent storage
- **In-Memory**: Temporary storage for development/testing (data lost on restart)

## Basic Usage

```python
from ollama_agents import Agent, SQLiteMemoryStore

# Create an agent with memory enabled
agent = Agent(
    name="my_agent",
    instructions="You are a helpful assistant.",
    enable_memory=True,
    memory_store=SQLiteMemoryStore("agent_data.db")  # Optional: specify storage backend
)

# Store information
agent.remember("user_name", "John Doe")
agent.remember("preferences", {"color": "blue", "food": "pizza"})

# Retrieve information
name = agent.recall("user_name")
preferences = agent.recall("preferences")

# Store with expiration (expires in 3600 seconds = 1 hour)
agent.remember("temp_token", "abc123", expires_in=3600)

# Store with metadata
agent.remember("sensitive_data", "secret", metadata={"sensitivity": "high"})

# List all memory keys for the agent
keys = agent.get_memory_keys()

# Delete specific memory
agent.forget("user_name")

# Clear all memory for the agent
agent.clear_memory()
```

## Memory Methods

- `remember(key, value, expires_in=None, metadata=None)`: Store a value in memory
- `recall(key)`: Retrieve a value from memory
- `forget(key)`: Delete a specific memory entry
- `get_memory_keys()`: List all memory keys for the agent
- `clear_memory()`: Clear all memory for the agent
- `get_memory_metadata(key)`: Get metadata for a memory entry
- `cleanup_expired_memory()`: Remove expired memory entries

## Memory Isolation

Each agent has its own isolated memory space. Agents cannot access each other's memory.

## Storage Backends

### SQLite
```python
from ollama_agents import SQLiteMemoryStore
store = SQLiteMemoryStore("path/to/database.db")  # File-based
# or
store = SQLiteMemoryStore(":memory:")  # In-memory (temporary)
```

### Redis (requires redis package)
```python
from ollama_agents import RedisMemoryStore
store = RedisMemoryStore(host='localhost', port=6379, db=0)
```

### PostgreSQL (requires psycopg2 package)
```python
from ollama_agents import PostgresMemoryStore
store = PostgresMemoryStore("postgresql://user:password@localhost/dbname")
```

### In-Memory (for temporary storage)
```python
from ollama_agents import InMemoryStore
store = InMemoryStore()
```

## Thread Safety

All memory stores are thread-safe and can be used in multi-threaded applications.

## Metadata

Memory entries can include metadata for additional context and categorization:

```python
agent.remember("user_email", "user@example.com", 
               metadata={"sensitivity": "high", "category": "contact_info"})
```

## Expiration

Memory entries can be set to expire automatically:

```python
# Expires in 1 hour (3600 seconds)
agent.remember("session_token", "token123", expires_in=3600)
```