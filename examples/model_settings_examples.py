"""
Examples demonstrating the new model configuration patterns in Ollama Agents SDK
"""
from ollama_agents import (
    Agent, AgentConfig, ModelSettings, DEFAULT_SETTINGS, 
    SIMPLE_CHAT_SETTINGS, CREATIVE_SETTINGS, PRECISE_SETTINGS,
    create_agent_with_settings, create_specialized_agent, AgentSession,
    tool, TraceLevel
)


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


def model_settings_example():
    print("=== Model Settings Configuration Example ===")
    
    # Example 1: Using the new ModelSettings pattern
    print("\n--- Example 1: Creating agent with custom ModelSettings ---")
    
    # Create custom settings
    custom_settings = ModelSettings(
        temperature=0.8,
        max_tokens=1024,
        top_p=0.9,
        frequency_penalty=0.1,
        presence_penalty=0.1,
        num_ctx=4096,  # Ollama-specific parameter
        seed=123
    )
    
    # Create agent with custom settings
    agent = create_agent_with_settings("qwen3-vl:2b-thinking-q8_0", custom_settings)
    agent.add_tool(add_numbers)
    
    response = agent.chat("What is 24 plus 18?")
    print(f"Response: {response['content']}")
    
    # Example 2: Using predefined settings
    print("\n--- Example 2: Using predefined settings ---")
    
    # Creative agent
    creative_agent = create_specialized_agent("creative", "qwen3-vl:2b-thinking-q8_0")
    creative_response = creative_agent.chat("Write a short creative story about a robot learning to paint")
    print(f"Creative response (first 100 chars): {creative_response['content'][:100]}...")
    
    # Precise agent
    precise_agent = create_specialized_agent("precise", "qwen3-vl:2b-thinking-q8_0")
    precise_response = precise_agent.chat("What is the capital of France?")
    print(f"Precise response: {precise_response['content']}")
    
    # Example 3: Merging settings
    print("\n--- Example 3: Merging settings ---")
    
    base_settings = ModelSettings(temperature=0.5, max_tokens=512)
    override_settings = ModelSettings(temperature=0.9, top_p=0.9)  # Override temperature
    
    from ollama_agents import merge_settings
    merged_settings = merge_settings(base_settings, override_settings)
    
    print(f"Base temperature: {base_settings.temperature}")
    print(f"Override temperature: {override_settings.temperature}")
    print(f"Merged temperature: {merged_settings.temperature}")
    print(f"Merged top_p: {merged_settings.top_p}")
    
    # Create agent with merged settings
    merged_agent = create_agent_with_settings("qwen3-vl:2b-thinking-q8_0", merged_settings)
    merged_response = merged_agent.chat("Tell me a joke")
    print(f"Merged agent response (first 80 chars): {merged_response['content'][:80]}...")


def agent_session_example():
    print("\n=== Agent Session Example ===")
    
    # Create different specialized agents
    creative_agent = create_specialized_agent("creative", "qwen3-vl:2b-thinking-q8_0")
    precise_agent = create_specialized_agent("precise", "qwen3-vl:2b-thinking-q8_0")
    simple_agent = create_specialized_agent("simple", "qwen3-vl:2b-thinking-q8_0")
    
    # Create an agent session
    agents = {
        "creative": creative_agent,
        "precise": precise_agent,
        "simple": simple_agent
    }
    session = AgentSession(agents)
    
    # Set context that can be shared across agents
    session.set_context("user_name", "Alice")
    session.set_context("task", "writing a story")
    
    # Use different agents for different parts of the task
    print("\n--- Using precise agent for facts ---")
    fact_response = session.run_with_agent("precise", 
        lambda agent: agent.chat("What year was the first computer invented?"))
    print(f"Fact: {fact_response['content']}")
    
    print("\n--- Using creative agent for story ---")
    story_context = session.get_context("task")
    user_name = session.get_context("user_name")
    
    story_response = session.run_with_agent("creative", 
        lambda agent: agent.chat(f"Write a short story about {user_name} discovering an old computer from {fact_response['content'][:4]}"))
    print(f"Story (first 120 chars): {story_response['content'][:120]}...")
    
    print("\n--- Using simple agent for summary ---")
    summary_response = session.run_with_agent("simple",
        lambda agent: agent.chat(f"Summarize this in one sentence: {story_response['content'][:200]}"))
    print(f"Summary: {summary_response['content']}")


def advanced_configuration_example():
    print("\n=== Advanced Configuration Example ===")
    
    # Example with Ollama-specific parameters
    ollama_specific_settings = ModelSettings(
        temperature=0.7,
        max_tokens=2048,
        # Ollama-specific parameters
        num_ctx=8192,        # Context window size
        num_gpu=1,           # Number of GPUs to use
        num_thread=8,        # Number of threads
        repeat_penalty=1.1,  # Penalty for repetition
        top_k=40,            # Limits next selection to top k tokens
        tfs_z=0.95,          # Tail free sampling
        typical_p=0.95,      # Typical probability sampling
        mirostat=2,          # Mirostat algorithm
        mirostat_tau=5.0,    # Mirostat target entropy
        mirostat_eta=0.1,    # Mirostat learning rate
        penalize_newline=True,  # Penalize newlines
        stop=["\n\n"]        # Stop sequence
    )
    
    advanced_agent = create_agent_with_settings("qwen3-vl:2b-thinking-q8_0", ollama_specific_settings)
    
    response = advanced_agent.chat("Explain quantum computing in simple terms")
    print(f"Advanced config response (first 150 chars): {response['content'][:150]}...")
    
    # Example with extra parameters
    print("\n--- Example with extra parameters ---")
    extra_params_settings = ModelSettings(
        temperature=0.5,
        extra_args={
            "mirostat_eta": 0.2,
            "mirostat_tau": 4.0,
            "num_keep": 16
        }
    )
    
    extra_agent = create_agent_with_settings("qwen3-vl:2b-thinking-q8_0", extra_params_settings)
    extra_response = extra_agent.chat("What are the benefits of renewable energy?")
    print(f"Extra params response (first 100 chars): {extra_response['content'][:100]}...")


def tracing_with_new_config_example():
    print("\n=== Tracing with New Configuration Example ===")
    
    # Create an agent with verbose tracing
    tracing_settings = ModelSettings(
        temperature=0.7,
        max_tokens=512,
        verbosity="high"  # Custom verbosity setting
    )
    
    agent = create_agent_with_settings(
        "qwen3-vl:2b-thinking-q8_0", 
        tracing_settings,
        trace_level=TraceLevel.VERBOSE
    )
    
    # Start a trace session
    from ollama_agents import start_global_trace_session
    session_id = start_global_trace_session()
    
    # Perform operations
    response1 = agent.chat("What is machine learning?")
    response2 = agent.generate("Explain neural networks briefly")
    
    # Export and show trace
    trace_json = agent.export_trace_session(session_id)
    print(f"Trace contains {len(trace_json)} characters")
    print(f"First 200 chars of trace: {trace_json[:200]}...")
    
    # End trace session
    from ollama_agents import end_global_trace_session
    end_global_trace_session()


def context_manager_example():
    print("\n=== Context Manager Example ===")
    
    # Sync context manager
    settings = ModelSettings(temperature=0.7)
    with create_agent_with_settings("qwen3-vl:2b-thinking-q8_0", settings) as agent:
        response = agent.chat("Hello, how are you?")
        print(f"Context manager response: {response['content'][:80]}...")
    
    # The agent is properly cleaned up after the context
    print("Agent context manager exited successfully")


if __name__ == "__main__":
    model_settings_example()
    agent_session_example()
    advanced_configuration_example()
    tracing_with_new_config_example()
    context_manager_example()
    
    print("\nAll new configuration examples completed!")