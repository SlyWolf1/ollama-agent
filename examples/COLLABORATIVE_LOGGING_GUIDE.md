# Collaborative Agents Logging Guide

The `collaborative_agents_example.py` has been enhanced with comprehensive logging, tracing, and statistics tracking to help you monitor and debug the multi-agent system.

## Features Added

### 1. **Comprehensive Logging** 📝

All agents and tools now include detailed logging at multiple levels:

- **INFO**: High-level operations (agent creation, routing decisions, results)
- **DEBUG**: Detailed information (parameters, response previews, tool calls)
- **WARNING**: Issues that don't stop execution (missing API keys)
- **ERROR**: Failures and exceptions

### 2. **Distributed Tracing** 🔍

Each agent has tracing enabled to track:
- Request/response flow
- Tool execution timing
- Agent handoffs
- Performance metrics

### 3. **Statistics Tracking** 📊

Automatic tracking of:
- Number of requests per agent
- Tool usage counts
- Response times
- Token usage
- Success/failure rates

## Configuration

The example is configured with:

```python
# Logging level (shows all messages)
set_global_log_level(LogLevel.DEBUG)

# Tracing level (detailed execution traces)
set_global_tracing_level(TraceLevel.VERBOSE)

# Statistics tracking
enable_stats()
```

### Log Levels

Change the logging verbosity:

```python
from ollama_agents import LogLevel, set_global_log_level

# Options:
set_global_log_level(LogLevel.DEBUG)    # Most verbose
set_global_log_level(LogLevel.INFO)     # Standard operations
set_global_log_level(LogLevel.WARNING)  # Only warnings/errors
set_global_log_level(LogLevel.ERROR)    # Only errors
```

### Trace Levels

Change the tracing detail:

```python
from ollama_agents import TraceLevel, set_global_tracing_level

# Options:
set_global_tracing_level(TraceLevel.VERBOSE)   # Full detail
set_global_tracing_level(TraceLevel.STANDARD)  # Standard info
set_global_tracing_level(TraceLevel.MINIMAL)   # Basic only
set_global_tracing_level(TraceLevel.OFF)       # Disabled
```

## What Gets Logged

### Agent Creation

```
INFO  �� Creating file search agent...
INFO  ✅ File search agent created: file_search_agent
DEBUG    Model: qwen2.5-coder:3b-instruct-q8_0
DEBUG    Tools: 3
DEBUG    Tracing: True
```

### Tool Execution

```
INFO  🔍 Searching vector store: query='API docs', limit=5
DEBUG Connecting to Qdrant at localhost:6333
DEBUG Searching collection 'vector_store' for: API docs
INFO  Found 5 results from vector store
```

### Query Routing

```
INFO  📂 Routing to file search agent: 'search our docs'
INFO  ✅ File search agent responded (1234 chars)
DEBUG Response preview: Here are the results...
```

### Errors

```
ERROR ❌ Error searching vector store: Connection refused
WARNING ⚠️ Web search agent created without API key
```

## Usage Examples

### Running with Full Logging

```bash
python3 examples/collaborative_agents_example.py
```

Output will show:
- Agent creation logs
- Example query processing (commented out by default)
- Instructions for interactive mode

### Interactive Mode with Logging

Uncomment the interactive section in the code:

```python
# In collaborative_agents_example.py
# Remove the # """ and """ # to enable interactive mode

while True:
    user_query = input("\n🤔 Your query: ").strip()
    # ...
```

Then run:

```bash
python3 examples/collaborative_agents_example.py
```

You'll see detailed logs for each query:

```
[22:44:49] INFO  User query: search for API docs
           INFO  🎯 Triage agent analyzing query...
           INFO  📂 Routing to file search agent: 'search for API docs'
           INFO  🔍 Searching vector store: query='API docs', limit=5
           INFO  Found 3 results from vector store
           INFO  ✅ File search agent responded (456 chars)
           INFO  Query completed successfully
```

### Viewing Statistics

At the end of a session, statistics are automatically printed:

```
📊 SESSION STATISTICS
================================================================================

file_search_agent:
  REQUESTS_MADE: 5
  TOOLS_CALLED: 3
  RESPONSE_TIME: 2.34s
  TOKENS_INPUT: 1234
  TOKENS_OUTPUT: 5678

web_search_agent:
  REQUESTS_MADE: 2
  ...

triage_agent:
  REQUESTS_MADE: 7
  ...
```

## Customizing Logging

### Per-Agent Logging

Each agent can have its own logging configuration:

```python
agent = Agent(
    name="my_agent",
    model="qwen2.5-coder:3b-instruct-q8_0",
    enable_tracing=True,              # Enable tracing
    trace_level=TraceLevel.VERBOSE    # Set trace detail level
)
```

### Tool-Level Logging

Add logging to your custom tools:

```python
from ollama_agents import tool, get_logger

logger = get_logger()

@tool("My custom tool")
def my_tool(query: str) -> str:
    logger.info(f"🔧 Tool called with: {query}")
    
    try:
        result = do_something(query)
        logger.info(f"✅ Tool completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Tool failed: {e}")
        raise
```

### Filtering Logs

Filter logs by component:

```python
# Get logger with specific name
logger = get_logger("my_component")

# All logs from this logger will be prefixed
logger.info("This is from my_component")
```

## Log Format

Logs include:
- **Timestamp**: `[12/30/25 22:44:49]`
- **Level**: `INFO`, `DEBUG`, `WARNING`, `ERROR`
- **Message**: The log content
- **Source**: File and line number (in DEBUG mode)

Example:
```
[12/30/25 22:44:49] INFO  ✅ Agent created: file_search_agent  logger.py:77
```

## Performance Impact

Logging has minimal performance impact:

- **LogLevel.ERROR**: ~0% overhead
- **LogLevel.WARNING**: ~1% overhead
- **LogLevel.INFO**: ~2-3% overhead
- **LogLevel.DEBUG**: ~5-10% overhead (lots of detail)

For production, use `LogLevel.INFO` or `LogLevel.WARNING`.

## Exporting Logs

### To File

Redirect output:

```bash
python3 examples/collaborative_agents_example.py > agent_logs.txt 2>&1
```

### Programmatic Export

```python
from ollama_agents import get_stats_tracker

# At end of session
stats = get_stats_tracker()
stats_json = stats.export_stats()

# Save to file
with open('agent_stats.json', 'w') as f:
    f.write(stats_json)
```

## Troubleshooting

### Too Much Output

Reduce logging level:

```python
set_global_log_level(LogLevel.INFO)  # Instead of DEBUG
set_global_tracing_level(TraceLevel.STANDARD)  # Instead of VERBOSE
```

### Missing Logs

Ensure logging is enabled:

```python
from ollama_agents import get_logger, LogLevel, set_global_log_level

# Enable logging
set_global_log_level(LogLevel.DEBUG)

# Verify logger works
logger = get_logger()
logger.info("Test log message")
```

### Logs Not Showing in Tools

Make sure to get the logger instance:

```python
from ollama_agents import get_logger

logger = get_logger()

@tool("My tool")
def my_tool():
    logger.info("This will show up")  # ✅
    print("This won't be logged")     # ❌ (only prints to console)
```

## Best Practices

1. **Use Appropriate Levels**
   - `DEBUG`: Development and troubleshooting
   - `INFO`: Normal operations
   - `WARNING`: Issues that should be noted
   - `ERROR`: Failures

2. **Add Context**
   ```python
   # Good
   logger.info(f"Processing query: '{query}' for agent: {agent_name}")
   
   # Bad
   logger.info("Processing")
   ```

3. **Log Boundaries**
   ```python
   logger.info("Starting operation X")
   # ... do work ...
   logger.info("Completed operation X")
   ```

4. **Use Emojis for Clarity**
   ```python
   logger.info("🔧 Creating...")
   logger.info("✅ Success")
   logger.error("❌ Failed")
   logger.warning("⚠️  Warning")
   ```

## Related Files

- `collaborative_agents_example.py` - Main example with full logging
- `test_collaborative_logging.py` - Simple logging test
- `COLLABORATIVE_AGENTS_README.md` - Main documentation

## Resources

- [Ollama Agents SDK Logging](../ollama_agents/logger.py)
- [Tracing Documentation](../ollama_agents/tracing.py)
- [Statistics Tracking](../ollama_agents/stats.py)
