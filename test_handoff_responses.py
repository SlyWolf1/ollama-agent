#!/usr/bin/env python3
"""
Test that agent handoffs preserve full LLM responses including errors
"""
from ollama_agents import (
    Agent, tool, ModelSettings,
    LogLevel, set_global_log_level, get_logger
)

set_global_log_level(LogLevel.INFO)
logger = get_logger()

print("=" * 80)
print("TESTING AGENT HANDOFF RESPONSES")
print("=" * 80)
print()

# Create a specialized agent that returns detailed error messages
specialized_agent = Agent(
    name="specialized_agent",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="""You are a helpful assistant. 
    
If someone asks about something unavailable, explain clearly:
- What was requested
- Why it's not available
- What they need to do to fix it
- Alternative solutions if any

Always be detailed and helpful in your explanations."""
)

# Create routing tool
@tool("Route to specialized agent")
def route_to_specialist(query: str) -> str:
    """Route query to specialized agent and return full response."""
    logger.info(f"🔀 Routing query: '{query}'")
    response = specialized_agent.chat(query)
    content = response.get('content', 'No response')
    logger.info(f"✅ Specialized agent responded ({len(content)} chars)")
    logger.debug(f"Full response: {content}")
    return content

# Create triage agent
triage_agent = Agent(
    name="triage_agent",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="""You coordinate with a specialized agent.

IMPORTANT: When you get a response from the specialized agent, show it COMPLETELY to the user.
Don't summarize, don't hide errors, don't shorten it.

Format: 
"Here's the response from the specialized agent:

[Full response here]"

Be transparent about everything.""",
    tools=[route_to_specialist]
)

# Test query
print("Testing with error scenario...")
print()

query = "Can you check the database for user information?"
print(f"Query: {query}")
print()

response = triage_agent.chat(query)
print("=" * 80)
print("TRIAGE AGENT RESPONSE:")
print("=" * 80)
print(response['content'])
print()

print("=" * 80)
print("✅ Test complete - check if full response is shown above")
print("=" * 80)
