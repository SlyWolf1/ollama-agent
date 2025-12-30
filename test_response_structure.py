#!/usr/bin/env python3
"""
Test to see response structure
"""
from ollama_agents import Agent, tool
import json

@tool("Test tool")
def test_tool(query: str) -> str:
    return f"Result: {query}"

agent = Agent(
    name="test",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="Use test_tool when asked.",
    tools=[test_tool]
)

# Make a call
print("Making call to agent...")
import ollama
response = ollama.chat(
    model="qwen2.5-coder:3b-instruct-q8_0",
    messages=[
        {"role": "system", "content": "Use test_tool when asked."},
        {"role": "user", "content": "use the test tool with query hello"}
    ],
    tools=[{
        "type": "function",
        "function": {
            "name": "test_tool",
            "description": "Test tool",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Query parameter"}
                },
                "required": ["query"]
            }
        }
    }]
)

print("\nResponse object attributes:")
print(f"  response.message: {response.message}")
print(f"  response.message.content: {response.message.content}")
print(f"  hasattr tool_calls: {hasattr(response.message, 'tool_calls')}")
if hasattr(response.message, 'tool_calls'):
    print(f"  response.message.tool_calls: {response.message.tool_calls}")
print(f"\nResponse.message dict: {response.message.__dict__ if hasattr(response.message, '__dict__') else 'no __dict__'}")
print(f"\nFull response dict:")
print(json.dumps(response.__dict__, indent=2, default=str))
