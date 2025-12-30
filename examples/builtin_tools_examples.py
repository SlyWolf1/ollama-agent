"""
Examples of using built-in tools with Ollama agents.
"""

from ollama_agents import Agent, get_tool_collection

# Example 1: File operations
print("=" * 80)
print("Example 1: File Tools")
print("=" * 80)

file_agent = Agent(
    name="file_assistant",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You help users with file operations. Use the tools to read, write, and list files.",
    tools=get_tool_collection("file")
)

# Test the agent
response = file_agent.chat("List the files in the current directory")
print(f"\n{response['content']}\n")

# Example 2: Data tools
print("=" * 80)
print("Example 2: Data Tools")
print("=" * 80)

data_agent = Agent(
    name="data_processor",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You process and manipulate data. Use JSON and calculation tools.",
    tools=get_tool_collection("data")
)

response = data_agent.chat("Calculate 25 * 47 + 123")
print(f"\n{response['content']}\n")

# Example 3: Text tools
print("=" * 80)
print("Example 3: Text Tools")
print("=" * 80)

text_agent = Agent(
    name="text_processor",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You process text. Count words, change case, etc.",
    tools=get_tool_collection("text")
)

response = text_agent.chat("Count how many words are in: The quick brown fox jumps over the lazy dog")
print(f"\n{response['content']}\n")

# Example 4: System tools
print("=" * 80)
print("Example 4: System Tools")
print("=" * 80)

system_agent = Agent(
    name="system_helper",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You help with system information. Get time, environment variables, etc.",
    tools=get_tool_collection("system")
)

response = system_agent.chat("What time is it right now?")
print(f"\n{response['content']}\n")

# Example 5: All tools
print("=" * 80)
print("Example 5: Multi-purpose Agent with All Tools")
print("=" * 80)

multi_agent = Agent(
    name="multi_agent",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="""You are a versatile assistant with access to many tools:
    - File operations (read, write, list)
    - Data processing (JSON, calculations)
    - Text processing (count words/chars, case conversion)
    - System information (time, environment)
    
    Use the appropriate tools to help the user.""",
    tools=get_tool_collection("all")
)

response = multi_agent.chat("Get the current time and tell me how many characters are in 'Hello World'")
print(f"\n{response['content']}\n")

print("=" * 80)
print("✅ Built-in tools examples complete!")
print("=" * 80)
