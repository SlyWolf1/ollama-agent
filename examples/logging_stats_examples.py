"""
Examples demonstrating logging and statistics tracking in Ollama Agents SDK
"""
from ollama_agents import (
    Agent, AgentConfig, ModelSettings, DEFAULT_SETTINGS,
    create_agent_with_settings, AgentHandoff, TraceLevel,
    get_stats_tracker, get_logger, LogLevel, StatType
)
import json


def logging_example():
    print("=== Logging Example ===")
    
    # Set up logging
    logger = get_logger()
    logger.info("Starting logging example")
    
    # Create an agent
    settings = ModelSettings(temperature=0.7)
    agent = create_agent_with_settings("qwen3-vl:2b-thinking-q8_0", settings)
    
    # Perform some operations that will generate logs
    response1 = agent.chat("Hello, how are you?")
    print(f"Response 1: {response1['content'][:50]}...")
    
    response2 = agent.generate("Tell me about artificial intelligence")
    print(f"Response 2: {response2['content'][:50]}...")
    
    logger.info("Completed basic operations")


def stats_tracking_example():
    print("\n=== Statistics Tracking Example ===")
    
    # Get the global stats tracker
    stats_tracker = get_stats_tracker()
    
    # Create an agent
    settings = ModelSettings(temperature=0.7)
    agent = create_agent_with_settings("qwen3-vl:2b-thinking-q8_0", settings)
    
    print("Initial stats:")
    initial_stats = agent.get_stats()
    for stat_type, value in initial_stats.items():
        if value > 0:  # Only show non-zero stats
            print(f"  {stat_type.value}: {value}")
    
    # Perform some operations
    print("\nPerforming operations...")
    response1 = agent.chat("What is the capital of France?")
    response2 = agent.chat("What is 15 plus 23?")
    response3 = agent.generate("Explain quantum computing briefly")
    
    # Get updated stats
    print("\nUpdated stats:")
    updated_stats = agent.get_stats()
    for stat_type, value in updated_stats.items():
        if value > 0:  # Only show non-zero stats
            print(f"  {stat_type.value}: {value}")
    
    # Get token usage
    token_usage = agent.get_token_usage()
    print(f"\nToken usage: {token_usage}")
    
    # Export stats to JSON
    stats_json = agent.export_stats()
    print(f"\nExported stats (first 200 chars): {stats_json[:200]}...")


def advanced_stats_example():
    print("\n=== Advanced Statistics Example ===")
    
    # Create agents with different configurations
    creative_settings = ModelSettings(temperature=0.9, max_tokens=1024)
    precise_settings = ModelSettings(temperature=0.3, max_tokens=512)
    
    creative_agent = create_agent_with_settings("qwen3-vl:2b-thinking-q8_0", creative_settings)
    precise_agent = create_agent_with_settings("qwen3-vl:2b-thinking-q8_0", precise_settings)
    
    # Perform operations with both agents
    print("Using creative agent...")
    creative_response = creative_agent.chat("Write a short creative story")
    
    print("Using precise agent...")
    precise_response = precise_agent.chat("What is the square root of 144?")
    
    # Compare stats between agents
    print("\nCreative agent stats:")
    creative_stats = creative_agent.get_stats()
    for stat_type, value in list(creative_stats.items())[:5]:  # Show first 5 stats
        if value > 0:
            print(f"  {stat_type.value}: {value}")
    
    print("\nPrecise agent stats:")
    precise_stats = precise_agent.get_stats()
    for stat_type, value in list(precise_stats.items())[:5]:  # Show first 5 stats
        if value > 0:
            print(f"  {stat_type.value}: {value}")
    
    # Export detailed stat records
    print("\nDetailed stat records for creative agent:")
    records_json = creative_agent.export_stat_records()
    records = json.loads(records_json)
    for record in records[:3]:  # Show first 3 records
        print(f"  {record['stat_type']}: {record['value']} at {record['timestamp']}")


def handoff_stats_example():
    print("\n=== Handoff Statistics Example ===")
    
    # Create specialized agents
    math_agent = create_agent_with_settings("qwen3-vl:2b-thinking-q8_0", ModelSettings(temperature=0.5))
    general_agent = create_agent_with_settings("qwen3-vl:2b-thinking-q8_0", ModelSettings(temperature=0.7))
    
    # Create handoff manager
    agents = {"math": math_agent, "general": general_agent}
    handoff_manager = AgentHandoff(agents)
    
    # Perform handoffs and operations
    handoff_manager.set_current_agent("general")
    
    # This should stay with general agent
    response1 = handoff_manager.chat_with_current("What is the weather like today?")
    print(f"General response: {response1['content'][:50]}...")
    
    # Perform a handoff
    handoff_result = handoff_manager.handoff_to("math", context={"reason": "math calculation needed"})
    print(f"Handoff result: {handoff_result['message']}")
    
    # Chat with math agent
    response2 = handoff_manager.chat_with_current("What is 24 times 18?")
    print(f"Math response: {response2['target_agent'].messages[-1]['content'][:50]}...")
    
    # Check handoff manager stats
    print("\nHandoff manager stats:")
    handoff_stats = handoff_manager.get_stats()
    for stat_type, value in handoff_stats.items():
        if value > 0:
            print(f"  {stat_type.value}: {value}")
    
    # Check individual agent stats
    print("\nMath agent stats after handoff:")
    math_stats = math_agent.get_stats()
    for stat_type, value in math_stats.items():
        if value > 0:
            print(f"  {stat_type.value}: {value}")


def token_usage_example():
    print("\n=== Token Usage Example ===")
    
    # Create an agent
    agent = create_agent_with_settings("qwen3-vl:2b-thinking-q8_0", ModelSettings(temperature=0.7))
    
    # Perform operations and track token usage
    print("Initial token usage:", agent.get_token_usage())
    
    response1 = agent.chat("Explain machine learning in detail")
    print("After first chat:", agent.get_token_usage())
    
    response2 = agent.generate("Write a long poem about technology")
    print("After generation:", agent.get_token_usage())
    
    response3 = agent.chat("Summarize our conversation")
    print("After second chat:", agent.get_token_usage())
    
    # Show total usage
    final_usage = agent.get_token_usage()
    print(f"\nTotal tokens used: {final_usage['total_tokens']}")
    print(f"Input tokens: {final_usage['prompt_tokens']}")
    print(f"Output tokens: {final_usage['completion_tokens']}")


def detailed_stats_analysis():
    print("\n=== Detailed Stats Analysis Example ===")
    
    # Create an agent
    agent = create_agent_with_settings("qwen3-vl:2b-thinking-q8_0", ModelSettings(temperature=0.7))
    
    # Perform various operations
    operations = [
        ("chat", "What is artificial intelligence?"),
        ("generate", "Explain neural networks briefly"),
        ("chat", "What are the benefits of renewable energy?"),
        ("generate", "Write a short story about a robot"),
        ("chat", "Explain quantum computing")
    ]
    
    for op_type, prompt in operations:
        if op_type == "chat":
            agent.chat(prompt)
        else:
            agent.generate(prompt)
    
    # Analyze the statistics
    stats = agent.get_stats()
    
    print("Operation Statistics:")
    print(f"  Requests made: {stats[StatType.REQUESTS_MADE]}")
    print(f"  Conversation turns: {stats[StatType.CONVERSATION_TURNS]}")
    print(f"  Tools called: {stats[StatType.TOOLS_CALLED]}")
    print(f"  Tools successful: {stats[StatType.TOOLS_SUCCESS]}")
    print(f"  Input tokens: {stats[StatType.TOKENS_INPUT]}")
    print(f"  Output tokens: {stats[StatType.TOKENS_OUTPUT]}")
    print(f"  Total tokens: {stats[StatType.TOKENS_TOTAL]}")
    
    # Calculate average response time if available
    if stats[StatType.RESPONSE_TIME] > 0 and stats[StatType.REQUESTS_MADE] > 0:
        avg_response_time = stats[StatType.RESPONSE_TIME] / stats[StatType.REQUESTS_MADE]
        print(f"  Average response time: {avg_response_time:.2f}s")
    
    # Export detailed analysis
    print("\nExporting detailed statistics...")
    stats_json = agent.export_stats()
    detailed_records = agent.export_stat_records()
    
    print(f"Full stats export: {len(stats_json)} characters")
    print(f"Detailed records: {len(detailed_records)} characters")


if __name__ == "__main__":
    logging_example()
    stats_tracking_example()
    advanced_stats_example()
    handoff_stats_example()
    token_usage_example()
    detailed_stats_analysis()
    
    print("\nAll logging and stats examples completed!")