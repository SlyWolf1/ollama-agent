"""
Examples demonstrating the Ollama Agents SDK features
"""
import asyncio
from ollama_agents import Agent, AgentHandoff, tool, ThinkingMode, ModelSettings


# Example 1: Basic Agent with Thinking Modes
def basic_agent_example():
    print("=== Basic Agent with Thinking Modes ===")
    
    # Create a simple agent
    agent = Agent(
        name="simple_agent",
        model="qwen2.5-coder:3b-instruct-q8_0",
        instructions="You are a helpful assistant that explains concepts clearly.",
        settings=ModelSettings(max_tokens=2000,thinking_mode=ThinkingMode.NONE),
        timeout=3000,
        enable_tracing=False
    )
    
    response = agent.chat("What is artificial intelligence?")
    print(f"Response: {response['content'][:200]}...")
    print()


# Example 2: Agent with Custom Tools
def tool_usage_example():
    print("=== Agent with Custom Tools ===")
    
    # Define some tools
    @tool("Calculate the sum of two numbers")
    def add_numbers(a: int, b: int) -> int:
        """
        Calculate the sum of two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            int: The sum of a and b
        """
        return a + b
    
    @tool("Get the length of a string")
    def get_length(text: str) -> int:
        """
        Get the length of a string.
        
        Args:
            text: Input string
            
        Returns:
            int: Length of the string
        """
        return len(text)
    
    # Create an agent with tools
    agent = Agent(
        name="calculator_agent",
        model="qwen2.5-coder:3b-instruct-q8_0",
        instructions="You are a helpful calculator assistant.",
        tools=[add_numbers, get_length],
        enable_tracing=False
    )
    
    response = agent.chat("What is 15 plus 23?")
    print(f"Response: {response['content']}")
    print()


# Example 3: Agent Handoff
def handoff_example():
    print("=== Agent Handoff Example ===")
    
    # Create different specialized agents
    math_agent = Agent(
        name="math_agent",
        model="qwen2.5-coder:3b-instruct-q8_0",
        instructions="You are a math expert who solves mathematical problems.",
        enable_tracing=False,
        settings=ModelSettings(max_tokens=2000,thinking_mode=ThinkingMode.NONE)
    )
    
    general_agent = Agent(
        name="general_agent",
        model="qwen2.5-coder:3b-instruct-q8_0", 
        instructions="You are a general knowledge assistant.",
        enable_tracing=False
    )
    
    # Create handoff manager
    agents = {
        "math": math_agent,
        "general": general_agent
    }
    handoff_manager = AgentHandoff(agents)
    
    # Set initial agent
    handoff_manager.set_current_agent("general")
    
    # Add a handoff rule: if message contains "calculate" or "math", handoff to math agent
    handoff_manager.add_handoff_rule(
        lambda msg: "calculate" in msg.lower() or "math" in msg.lower(),
        "math",
        priority=1
    )
    
    # Chat with general agent - should trigger handoff
    response = handoff_manager.chat_with_current("Can you calculate 15 times 25 for me?")
    
    # Check if handoff occurred
    if "target_agent" in response:
        print(f"Handoff triggered: {response['message']}")
        # Now chat with the target agent
        target_agent = response["target_agent"]
        final_response = target_agent.chat("What is 15 times 25?")
        print(f"Response: {final_response['content']}")
    elif "content" in response:
        print(f"Response: {response['content']}")
    else:
        print(f"Unexpected response format: {response}")
    print()


# Example 4: Advanced Thinking Modes
def thinking_modes_example():
    print("=== Advanced Thinking Modes ===")
    
    # Create agents with different thinking modes using direct parameters
    quick_agent = Agent(
        name="quick_agent",
        model="qwen2.5-coder:3b-instruct-q8_0",
        instructions="Provide brief, concise answers.",
        max_tokens=1000,
        temperature=0.7
    )
    
    deep_agent = Agent(
        name="deep_agent",
        model="qwen2.5-coder:3b-instruct-q8_0", 
        instructions="Provide detailed, comprehensive answers with reasoning.",
        max_tokens=2000,
        temperature=0.8,
        thinking_mode=ThinkingMode.HIGH  # Enable thinking for deeper reasoning
    )
    
    question = "Why is the sky blue?"
    
    print("Quick thinking response:")
    quick_response = quick_agent.chat(question)
    print(f"{quick_response['content'][:150]}...")
    
    print("\nDeep thinking response:")
    deep_response = deep_agent.chat(question)
    print(f"{deep_response['content'][:150]}...")
    print()


# Example 5: Asynchronous Operations
async def async_example():
    print("=== Asynchronous Operations ===")
    
    agent = Agent(
        name="async_agent",
        model="qwen2.5-coder:3b-instruct-q8_0",
        instructions="You are an async assistant.",
        max_tokens=1500,
        temperature=0.7
    )
    
    response = await agent.achat("What can you tell me about async programming?")
    print(f"Async response: {response['content'][:150]}...")
    print()


if __name__ == "__main__":
    basic_agent_example()
    tool_usage_example()
    handoff_example()
    # thinking_modes_example()
    
    # Run async example
    asyncio.run(async_example())
    
    print("All examples completed!")
