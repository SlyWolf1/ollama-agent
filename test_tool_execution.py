#!/usr/bin/env python3
"""
Test tool execution with detailed logging
"""
from ollama_agents import (
    Agent, tool, ThinkingMode, ModelSettings,
    TraceLevel, set_global_tracing_level, LogLevel, set_global_log_level,
    enable_stats, get_logger
)

# Enable comprehensive logging
set_global_log_level(LogLevel.DEBUG)
set_global_tracing_level(TraceLevel.VERBOSE)
enable_stats()

logger = get_logger()

print("=" * 80)
print("TESTING TOOL EXECUTION WITH LOGGING")
print("=" * 80)
print()

# Create a simple tool that returns results
@tool("Get information")
def get_info(query: str) -> str:
    """Get information based on a query."""
    logger.info(f"🔧 get_info tool called with query: '{query}'")
    result = f"Here is the information about: {query}\n- Detail 1\n- Detail 2\n- Detail 3"
    logger.info(f"🔧 get_info returning result ({len(result)} chars)")
    return result

# Create routing tool
@tool("Route to info agent")
def route_to_info(query: str) -> str:
    """Route query to info agent."""
    logger.info(f"🔀 route_to_info called with: '{query}'")
    info_agent = Agent(
        name="info_agent",
        model="qwen2.5-coder:3b-instruct-q8_0",
        instructions="You are an information agent. Use get_info tool to answer questions.",
        tools=[get_info]
    )
    response = info_agent.chat(query)
    logger.info(f"🔀 route_to_info got response ({len(response['content'])} chars)")
    return response['content']

# Create triage agent
print("Creating triage agent...")
triage_agent = Agent(
    name="triage_agent",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You route queries to the info agent using the route_to_info tool.",
    tools=[route_to_info],
    enable_tracing=True,
    trace_level=TraceLevel.VERBOSE
)

print(f"✅ Triage agent created with {len(triage_agent.tool_registry.tools)} tools")
print(f"   Tools: {list(triage_agent.tool_registry.tools.keys())}")
print()

# Test query
print("=" * 80)
print("SENDING TEST QUERY")
print("=" * 80)
print()

query = "give me info on Python programming"
print(f"Query: {query}")
print()

try:
    response = triage_agent.chat(query)
    
    print("=" * 80)
    print("RESPONSE")
    print("=" * 80)
    print(response['content'])
    print()
    
except Exception as e:
    logger.error(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
