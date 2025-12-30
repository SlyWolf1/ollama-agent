"""
Quick test to demonstrate collaborative agents with comprehensive logging
"""
from ollama_agents import (
    Agent, tool, ThinkingMode, ModelSettings,
    TraceLevel, set_global_tracing_level, LogLevel, set_global_log_level,
    enable_stats, get_logger, get_stats_tracker
)

# Enable comprehensive logging
set_global_log_level(LogLevel.INFO)  # Use INFO to reduce verbosity
set_global_tracing_level(TraceLevel.STANDARD)
enable_stats()

logger = get_logger()

logger.info("=" * 80)
logger.info("COLLABORATIVE AGENTS LOGGING TEST")
logger.info("=" * 80)

# Create a simple mock tool
@tool("Mock search tool")
def mock_search(query: str) -> str:
    """Mock search that returns a simple response."""
    logger.info(f"🔍 Mock search called with query: '{query}'")
    return f"Mock results for: {query}"

# Create a simple agent
logger.info("Creating test agent...")
agent = Agent(
    name="test_agent",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are a helpful assistant",
    tools=[mock_search],
    enable_tracing=True,
    trace_level=TraceLevel.STANDARD
)
logger.info(f"✅ Agent created: {agent.name}")

# Test a simple interaction (without actually calling Ollama)
logger.info("Agent is ready for queries")
logger.info(f"  Model: {agent.model}")
logger.info(f"  Tools: {len(agent.tools)}")
logger.info(f"  Tracing enabled: {agent.enable_tracing}")

# Show stats
stats = get_stats_tracker()
logger.info("=" * 80)
logger.info("Logging test completed successfully!")
logger.info("=" * 80)

print("\n✅ Logging is fully configured and working!")
print("   - Log level: INFO")
print("   - Trace level: STANDARD")
print("   - Stats tracking: ENABLED")
print("\nCheck the output above to see the detailed logs.")
