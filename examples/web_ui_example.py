"""
Example of using the Web UI for agent management.
Run this script and open http://localhost:5000 in your browser.
"""

from ollama_agents import Agent, tool, AgentManager, create_web_ui, get_tool_collection

print("=" * 80)
print("Web UI Example - Agent Management Dashboard")
print("=" * 80)

# Create agent manager
manager = AgentManager()

# Create some agents
print("\n📝 Creating agents...")

# 1. General assistant
assistant = Agent(
    name="assistant",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are a helpful general-purpose assistant."
)
manager.add_agent(assistant)
print("✅ Added: assistant")

# 2. Code helper
code_helper = Agent(
    name="code_helper",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are a coding assistant. Help with programming questions and write code.",
    tools=get_tool_collection("data")
)
manager.add_agent(code_helper)
print("✅ Added: code_helper")

# 3. File manager
file_manager = Agent(
    name="file_manager",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You help with file operations. Read, write, and list files.",
    tools=get_tool_collection("file")
)
manager.add_agent(file_manager)
print("✅ Added: file_manager")

# 4. Text processor
text_processor = Agent(
    name="text_processor",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You process and analyze text. Count words, change case, etc.",
    tools=get_tool_collection("text")
)
manager.add_agent(text_processor)
print("✅ Added: text_processor")

# 5. Data analyst
@tool("Analyze data")
def analyze_data(data: str) -> str:
    """Analyze data and provide insights"""
    return f"Analysis of: {data}\n- Length: {len(data)}\n- Words: {len(data.split())}"

analyst = Agent(
    name="data_analyst",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are a data analyst. Use tools to analyze data and provide insights.",
    tools=[analyze_data] + get_tool_collection("data")
)
manager.add_agent(analyst)
print("✅ Added: data_analyst")

print(f"\n✅ {len(manager.agents)} agents ready!")

# List agents
print("\n📋 Registered agents:")
for agent_info in manager.list_agents():
    print(f"  • {agent_info['name']}: {agent_info['tools']} tools, model={agent_info['model']}")

# Start web UI
print("\n" + "=" * 80)
print("🌐 Starting Web UI...")
print("=" * 80)
print("\n🌟 Open your browser and go to: http://localhost:5000")
print("\n💡 Features:")
print("  • Chat with different agents")
print("  • Switch between agents")
print("  • View conversation history")
print("  • See agent statistics")
print("\n⚠️  Press Ctrl+C to stop the server\n")
print("=" * 80)

try:
    create_web_ui(manager, host="0.0.0.0", port=5000)
except KeyboardInterrupt:
    print("\n\n👋 Shutting down Web UI...")
except ImportError:
    print("\n❌ Flask is required for Web UI")
    print("Install with: pip install flask")
    print("\nOr test without Web UI:")
    print("\nTesting agent manager...")
    
    # Test the manager without UI
    test_agent = "assistant"
    test_message = "Hello! How are you?"
    
    print(f"\n💬 Testing {test_agent}...")
    print(f"User: {test_message}")
    
    response = manager.chat(test_agent, test_message)
    print(f"Agent: {response.get('content', '')}")
    
    print("\n✅ Agent manager working! Install Flask to use Web UI.")
