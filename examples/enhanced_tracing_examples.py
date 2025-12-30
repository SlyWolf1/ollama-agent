"""
Examples demonstrating enhanced tracing with token metrics and performance tracking
"""
from ollama_agents import (
    EnhancedAgent, EnhancedAgentConfig, ModelSettings, DEFAULT_SETTINGS,
    create_agent_with_settings, AgentHandoff, TraceLevel,
    get_stats_tracker, get_logger, LogLevel, StatType,
    TokenUsage, PerformanceMetrics
)
from ollama_agents.tools import tool
import time


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
    time.sleep(0.1)  # Simulate some processing time
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


def enhanced_tracing_example():
    print("=== Enhanced Tracing with Token Metrics and Performance Tracking ===")
    
    # Create an agent with enhanced tracing
    settings = ModelSettings(temperature=0.7)
    config = EnhancedAgentConfig(
        model="llama3.2",
        model_settings=settings,
        trace_level=TraceLevel.VERBOSE
    )
    agent = EnhancedAgent(config)
    agent.add_tool(add_numbers)
    agent.add_tool(get_current_time)
    
    # Start a trace session
    from ollama_agents import start_global_trace_session
    session_id = start_global_trace_session()
    
    print("Performing operations with enhanced tracing...")
    
    # Perform a chat operation with tools
    response1 = agent.chat("What is 15 plus 23?")
    print(f"Response 1: {response1['content'][:50]}...")
    
    # Perform another operation
    response2 = agent.generate("Explain quantum computing in simple terms")
    print(f"Response 2: {response2['content'][:50]}...")
    
    # Perform a tool call
    response3 = agent.chat("What is the current time?")
    print(f"Response 3: {response3['content'][:50]}...")
    
    # Get trace store and analyze the data
    trace_store = agent.get_trace_store()
    events = trace_store.get_events(session_id)
    
    print(f"\nTraced {len(events)} events")
    
    # Analyze token usage
    token_summary = trace_store.get_token_usage_summary(session_id)
    print(f"\nToken Usage Summary:")
    print(f"  Prompt tokens: {token_summary.prompt_tokens}")
    print(f"  Completion tokens: {token_summary.completion_tokens}")
    print(f"  Total tokens: {token_summary.total_tokens}")
    
    # Analyze performance
    perf_summary = trace_store.get_performance_summary(session_id)
    print(f"\nPerformance Summary:")
    for key, value in perf_summary.items():
        print(f"  {key}: {value:.3f}")
    
    # Export and show trace
    trace_json = agent.export_trace_session(session_id)
    print(f"\nFull trace export: {len(trace_json)} characters")
    
    # End trace session
    from ollama_agents import end_global_trace_session
    end_global_trace_session()


def performance_metrics_example():
    print("\n=== Performance Metrics Example ===")
    
    # Create an agent
    agent = EnhancedAgent(EnhancedAgentConfig(model="llama3.2"))
    agent.add_tool(add_numbers)
    
    # Perform operations and measure performance
    print("Measuring performance metrics...")
    
    start_time = time.time()
    response = agent.chat("Calculate 99 plus 1")
    end_time = time.time()
    
    duration = end_time - start_time
    print(f"Operation completed in {duration:.3f}s")
    
    # Get token usage
    token_usage = agent.get_token_usage()
    print(f"Token usage: {token_usage}")
    
    # Get stats
    stats = agent.get_stats()
    print(f"Stats:")
    for stat_type, value in stats.items():
        if value > 0:
            print(f"  {stat_type.value}: {value}")


def tool_execution_timing_example():
    print("\n=== Tool Execution Timing Example ===")
    
    # Create an agent with tools
    agent = EnhancedAgent(EnhancedAgentConfig(model="llama3.2"))
    agent.add_tool(add_numbers)
    agent.add_tool(get_current_time)
    
    # Perform operations that use tools
    print("Performing operations with tool calls...")
    
    response = agent.chat("What is 100 plus 25?")
    print(f"Addition result: {response['content']}")
    
    response = agent.chat("What time is it now?")
    print(f"Time result: {response['content'][:50]}...")
    
    # Get trace store to see tool execution timing
    trace_store = agent.get_trace_store()
    events = trace_store.get_events()
    
    tool_events = [e for e in events if 'tool' in e.event_type]
    print(f"\nFound {len(tool_events)} tool-related events:")
    for event in tool_events:
        print(f"  {event.event_type}: {event.data}")
        if event.performance:
            print(f"    Performance: tokens/sec={event.performance.tokens_per_second}, response_time={event.performance.response_time}")


def comprehensive_tracing_example():
    print("\n=== Comprehensive Tracing Example ===")
    
    # Create specialized agents
    math_agent = EnhancedAgent(EnhancedAgentConfig(model="llama3.2", system_prompt="You are a math expert."))
    general_agent = EnhancedAgent(EnhancedAgentConfig(model="llama3.2", system_prompt="You are a general assistant."))
    
    # Add tools to math agent
    math_agent.add_tool(add_numbers)
    
    # Create handoff manager
    agents = {
        "math": math_agent,
        "general": general_agent
    }
    handoff_manager = AgentHandoff(agents)
    
    # Start tracing
    from ollama_agents import start_global_trace_session
    session_id = start_global_trace_session()
    
    # Set initial agent
    handoff_manager.set_current_agent("general")
    
    # Perform operations
    print("Chatting with general agent...")
    response1 = handoff_manager.chat_with_current("What is the weather like today?")
    print(f"General response: {response1['content'][:50]}...")
    
    # Perform a handoff
    print("\nPerforming handoff to math agent...")
    handoff_result = handoff_manager.handoff_to("math", context={"reason": "math calculation needed"})
    print(f"Handoff result: {handoff_result['message']}")
    
    # Perform math operation
    print("\nPerforming math operation with math agent...")
    math_response = handoff_manager.chat_with_current("What is 24 times 18?")
    print(f"Math result: {math_response['target_agent'].messages[-1]['content'][:50]}...")
    
    # Analyze the comprehensive trace
    trace_store = handoff_manager.get_trace_store()
    events = trace_store.get_events(session_id)
    
    print(f"\nTotal events traced: {len(events)}")
    
    # Categorize events
    event_types = {}
    for event in events:
        event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
    
    print(f"\nEvent types:")
    for event_type, count in event_types.items():
        print(f"  {event_type}: {count}")
    
    # Get token usage summary
    token_summary = trace_store.get_token_usage_summary(session_id)
    print(f"\nToken Summary:")
    print(f"  Total tokens: {token_summary.total_tokens}")
    print(f"  Prompt tokens: {token_summary.prompt_tokens}")
    print(f"  Completion tokens: {token_summary.completion_tokens}")
    
    # Get performance summary
    perf_summary = trace_store.get_performance_summary(session_id)
    print(f"\nPerformance Summary:")
    for key, value in perf_summary.items():
        print(f"  {key}: {value:.3f}")
    
    # End tracing
    from ollama_agents import end_global_trace_session
    end_global_trace_session()


def tokens_per_second_example():
    print("\n=== Tokens Per Second Calculation Example ===")
    
    # Create an agent
    agent = EnhancedAgent(EnhancedAgentConfig(model="llama3.2"))
    
    # Perform operations to generate tokens
    print("Generating content to measure tokens per second...")
    
    # Generate a longer response to get meaningful metrics
    response = agent.generate("Write a detailed explanation of how machine learning works, including supervised and unsupervised learning approaches. Make it comprehensive but concise, around 200 words.")
    
    print(f"Generated {len(response['content'])} characters")
    
    # Get trace events to see performance metrics
    trace_store = agent.get_trace_store()
    events = trace_store.get_events()
    
    generate_events = [e for e in events if e.event_type == "agent.generate"]
    for event in generate_events:
        if event.performance:
            print(f"Performance metrics for generation:")
            print(f"  Response time: {event.performance.response_time:.3f}s")
            if event.performance.tokens_per_second:
                print(f"  Tokens per second: {event.performance.tokens_per_second:.2f}")
            if event.performance.input_throughput:
                print(f"  Input throughput: {event.performance.input_throughput:.2f} tokens/sec")
            if event.performance.output_throughput:
                print(f"  Output throughput: {event.performance.output_throughput:.2f} tokens/sec")
        
        if event.token_usage:
            print(f"Token usage:")
            print(f"  Prompt: {event.token_usage.prompt_tokens}")
            print(f"  Completion: {event.token_usage.completion_tokens}")
            print(f"  Total: {event.token_usage.total_tokens}")


if __name__ == "__main__":
    enhanced_tracing_example()
    performance_metrics_example()
    tool_execution_timing_example()
    comprehensive_tracing_example()
    tokens_per_second_example()
    
    print("\nAll enhanced tracing examples completed!")