"""
Example demonstrating tracing functionality in Ollama Agents SDK
"""
import asyncio
from ollama_agents import Agent, AgentConfig, AgentHandoff, tool, ThinkingMode, TraceLevel, get_tracer, ModelSettings


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


@tool("Get the current time")
def get_current_time() -> str:
    """
    Get the current time.
    
    Returns:
        str: Current time in a human-readable format
    """
    import datetime
    return str(datetime.datetime.now())


def tracing_example():
    print("=== Tracing Example ===")
    
    # Start a trace session
    session_id = get_tracer().start_trace_session()
    print(f"Started trace session: {session_id}")
    
    # Create an agent with tracing enabled
    config = AgentConfig(
        model="qwen3-vl:2b-thinking-q8_0",
        system_prompt="You are a helpful assistant that can perform calculations.",
        model_settings=ModelSettings(thinking_mode=ThinkingMode.MEDIUM),
        trace_level=TraceLevel.VERBOSE  # Enable verbose tracing
    )
    
    agent = Agent(config)
    agent.add_tool(add_numbers)
    agent.add_tool(get_current_time)
    
    print("\n--- Agent with Tools ---")
    response = agent.chat("What is 15 plus 23?")
    print(f"Response: {response['content']}")
    
    print("\n--- Agent Generation ---")
    gen_response = agent.generate("Explain what artificial intelligence is in one sentence.")
    print(f"Generated: {gen_response['content']}")
    
    # Get and display trace information
    trace_store = agent.get_trace_store()
    events = trace_store.get_events(session_id)
    
    print(f"\n--- Trace Events ({len(events)} events) ---")
    for i, event in enumerate(events):
        print(f"{i+1}. {event.event_type} - Duration: {event.duration:.3f}s")
        if event.data:
            print(f"   Data: {event.data}")
    
    # Export trace to JSON
    json_trace = agent.export_trace_session(session_id)
    print(f"\n--- Exported Trace (first 300 chars) ---")
    print(json_trace[:300] + "..." if len(json_trace) > 300 else json_trace)
    
    # End the trace session
    get_tracer().end_trace_session()


def handoff_tracing_example():
    print("\n=== Handoff Tracing Example ===")
    
    # Start a trace session
    session_id = get_tracer().start_trace_session()
    print(f"Started trace session: {session_id}")
    
    # Create specialized agents
    math_agent_config = AgentConfig(
        model="qwen3-vl:2b-thinking-q8_0",
        system_prompt="You are a math expert.",
        trace_level=TraceLevel.STANDARD
    )
    math_agent = Agent(math_agent_config)
    
    general_agent_config = AgentConfig(
        model="qwen3-vl:2b-thinking-q8_0",
        system_prompt="You are a general knowledge assistant.",
        trace_level=TraceLevel.STANDARD
    )
    general_agent = Agent(general_agent_config)
    
    # Create handoff manager
    agents = {
        "math": math_agent,
        "general": general_agent
    }
    handoff_manager = AgentHandoff(agents)
    
    # Set initial agent
    handoff_manager.set_current_agent("general")
    
    # Add a handoff rule
    handoff_manager.add_handoff_rule(
        lambda msg: "calculate" in msg.lower() or "math" in msg.lower(),
        "math",
        priority=1
    )
    
    print("\n--- Chat with Handoff Trigger ---")
    response = handoff_manager.chat_with_current("Can you calculate 15 times 25 for me?")
    print(f"Response: {response['target_agent'].messages[-1]['content']}")
    
    # Get and display trace information
    trace_store = handoff_manager.get_trace_store()
    events = trace_store.get_events(session_id)
    
    print(f"\n--- Handoff Trace Events ({len(events)} events) ---")
    for i, event in enumerate(events):
        print(f"{i+1}. {event.event_type} - Agent: {event.agent_id}")
        if event.data:
            print(f"   Data: {event.data}")
    
    # End the trace session
    get_tracer().end_trace_session()


def tracing_levels_example():
    print("\n=== Tracing Levels Example ===")
    
    # Test different tracing levels
    for level in [TraceLevel.OFF, TraceLevel.MINIMAL, TraceLevel.STANDARD, TraceLevel.VERBOSE]:
        print(f"\n--- Testing {level.value} tracing level ---")
        
        session_id = get_tracer().start_trace_session()
        
        config = AgentConfig(
            model="qwen3-vl:2b-thinking-q8_0",
            system_prompt="You are a test assistant.",
            trace_level=level
        )
        
        agent = Agent(config)
        
        # Perform an action
        response = agent.chat("Hello, how are you?")
        print(f"Response received: {len(response['content'])} chars")
        
        # Check trace events
        trace_store = agent.get_trace_store()
        events = trace_store.get_events(session_id)
        print(f"Number of trace events: {len(events)}")
        
        get_tracer().end_trace_session()


if __name__ == "__main__":
    tracing_example()
    handoff_tracing_example()
    tracing_levels_example()
    
    print("\nTracing examples completed!")