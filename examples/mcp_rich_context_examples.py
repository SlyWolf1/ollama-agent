"""
Examples demonstrating MCP support, Rich logging, and context management in Ollama Agents SDK
"""
from ollama_agents import (
    Agent, AgentConfig, ModelSettings, DEFAULT_SETTINGS,
    AgentHandoff, TraceLevel, get_logger, LogLevel,
    MCPContext, MCPResource, MCPResourceType,
    ContextManager, TruncationStrategy
)
from ollama_agents.tools import tool


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


def mcp_example():
    print("=== MCP (Model Context Protocol) Example ===")
    
    # Create an agent with MCP context
    agent = Agent(AgentConfig(model="qwen3-vl:2b-thinking-q8_0"))
    agent.add_tool(add_numbers)
    agent.add_tool(get_current_time)
    
    # Add resources to the MCP context
    resource1 = MCPResource(
        uri="file://document.txt",
        type=MCPResourceType.DOCUMENT,
        name="example_document",
        description="An example document resource"
    )
    agent.mcp_context.context_manager.add_resource(resource1)
    
    # Register tools in MCP context
    agent.mcp_context.register_tool_from_registry(agent.tool_registry)
    
    # Export MCP context
    mcp_context_json = agent.mcp_context.export_mcp_context()
    print(f"MCP Context exported ({len(mcp_context_json)} chars)")
    
    # Perform operations
    response = agent.chat("What is 15 plus 23?")
    print(f"Response: {response['content']}")
    
    # Show MCP context
    print("\nMCP Context Resources:")
    for resource in agent.mcp_context.context_manager.get_resources():
        print(f"  - {resource.name}: {resource.description}")


def rich_logging_example():
    print("\n=== Rich Logging Example ===")
    
    # Get the rich logger
    logger = get_logger()
    
    # Log different types of messages
    logger.info("Starting rich logging example", agent_id="example_agent")
    logger.warning("This is a warning message", agent_id="example_agent")
    logger.error("This is an error message", agent_id="example_agent")
    
    # Create an agent and perform operations
    agent = Agent(AgentConfig(model="qwen3-vl:2b-thinking-q8_0"))
    agent.add_tool(add_numbers)
    
    # Log agent statistics
    stats = agent.get_stats()
    logger.log_agent_stats("example_agent", {k.value: v for k, v in stats.items() if v > 0})
    
    # Perform operations and log them
    response = agent.chat("What is 10 plus 5?")
    logger.log_tool_call("add_numbers", {"a": 10, "b": 5}, result=response['content'])
    
    # Log token usage
    token_usage = agent.get_token_usage()
    logger.log_token_usage(token_usage)


def context_truncation_example():
    print("\n=== Context Truncation Example ===")
    
    # Create an agent with limited context
    config = AgentConfig(
        model="qwen3-vl:2b-thinking-q8_0",
        max_context_length=500,  # Very small context for demonstration
        context_truncation_strategy=TruncationStrategy.SUMMARIZE_MIDDLE
    )
    agent = Agent(config)
    
    # Add a lot of messages to exceed context limit
    for i in range(10):
        agent.add_message("user", f"This is message number {i} in a long conversation that will exceed context limits.")
        agent.add_message("assistant", f"Response to message {i} showing how the system handles long conversations.")
    
    print(f"Context length before truncation: {sum(len(msg['content']) for msg in agent.messages)} characters")
    
    # Apply context management
    truncated_messages = agent.messages  # This would normally be processed by the context manager
    print(f"Number of messages: {len(agent.messages)}")
    
    # Show the context management in action
    context_manager = ContextManager(
        max_context_length=500,
        strategy=TruncationStrategy.OLDEST_FIRST
    )
    
    for msg in agent.messages:
        context_manager.add_message(msg["role"], msg["content"])
    
    truncated = context_manager.truncate_context(agent.client, agent.config.model)
    print(f"Messages after truncation: {len(truncated)}")
    
    # Perform an operation with the agent
    response = agent.chat("What have we been discussing?")
    print(f"Response: {response['content'][:100]}...")


def context_summarization_example():
    print("\n=== Context Summarization Example ===")
    
    # Create an agent with summarization settings
    config = AgentConfig(
        model="qwen3-vl:2b-thinking-q8_0",
        max_context_length=2000,
        context_truncation_strategy=TruncationStrategy.SUMMARIZE_MIDDLE
    )
    agent = Agent(config)
    
    # Add a conversation that would benefit from summarization
    topics = [
        "the weather today",
        "upcoming projects",
        "team meeting notes", 
        "budget planning",
        "new feature development"
    ]
    
    for i, topic in enumerate(topics):
        agent.add_message("user", f"Let's discuss {topic}. This is an important topic that requires detailed consideration.")
        agent.add_message("assistant", f"Regarding {topic}, we should consider multiple factors including timelines, resources, and potential challenges.")
    
    print(f"Context length: {sum(len(msg['content']) for msg in agent.messages)} characters")
    print(f"Should summarize: {agent.should_summarize_context()}")
    
    # Get a summary
    summary = agent.summarize_context()
    print(f"Summary: {summary[:150]}...")
    
    # Perform a chat with the summarized context
    response = agent.chat("Can you summarize our discussion?")
    print(f"Response: {response['content'][:100]}...")


def enhanced_handoff_example():
    print("\n=== Enhanced Handoff with Context Summarization ===")
    
    # Create specialized agents
    math_agent_config = AgentConfig(
        model="qwen3-vl:2b-thinking-q8_0",
        system_prompt="You are a math expert.",
        max_context_length=1000
    )
    math_agent = Agent(math_agent_config)
    math_agent.add_tool(add_numbers)
    
    general_agent_config = AgentConfig(
        model="qwen3-vl:2b-thinking-q8_0",
        system_prompt="You are a general knowledge assistant.",
        max_context_length=1000
    )
    general_agent = Agent(general_agent_config)
    
    # Add extensive conversation to general agent to trigger summarization
    for i in range(5):
        general_agent.add_message("user", f"This is conversation topic {i} about various subjects that will be summarized during handoff.")
        general_agent.add_message("assistant", f"Response to topic {i} with detailed information.")
    
    # Create handoff manager
    agents = {
        "math": math_agent,
        "general": general_agent
    }
    handoff_manager = AgentHandoff(agents)
    
    # Set initial agent
    handoff_manager.set_current_agent("general")
    
    print(f"General agent context length: {sum(len(msg['content']) for msg in general_agent.messages)} characters")
    
    # Perform handoff with context summarization
    result = handoff_manager.handoff_to(
        "math", 
        context={"reason": "math calculation needed"},
        use_context_summarization=True
    )
    
    print(f"Handoff completed to: {result['target_agent'].config.model}")
    
    # Perform operation with math agent
    math_response = result["target_agent"].chat("What is 99 plus 1?")
    print(f"Math agent response: {math_response['content']}")


def comprehensive_example():
    print("\n=== Comprehensive Example ===")
    
    # Create an agent with all new features enabled
    settings = ModelSettings(
        temperature=0.7,
        max_tokens=512
    )
    config = AgentConfig(
        model="qwen3-vl:2b-thinking-q8_0",
        model_settings=settings,
        trace_level=TraceLevel.VERBOSE,
        max_context_length=2000,
        context_truncation_strategy=TruncationStrategy.SUMMARIZE_MIDDLE
    )
    
    agent = Agent(config)
    agent.add_tool(add_numbers)
    agent.add_tool(get_current_time)
    
    # Add MCP resources
    doc_resource = MCPResource(
        uri="file://requirements.txt",
        type=MCPResourceType.FILE,
        name="project_requirements",
        description="Project requirements document"
    )
    agent.mcp_context.context_manager.add_resource(doc_resource)
    
    # Perform a series of operations
    logger = get_logger()
    logger.info("Starting comprehensive example", agent_id=agent.config.model)
    
    # Multiple interactions to build up context
    responses = []
    for i in range(3):
        response = agent.chat(f"Tell me about topic number {i} and its importance.")
        responses.append(response)
        logger.info(f"Interaction {i+1} completed", agent_id=agent.config.model)
    
    # Check context and stats
    context_length = sum(len(msg['content']) for msg in agent.messages)
    print(f"Final context length: {context_length} characters")
    
    stats = agent.get_stats()
    logger.log_agent_stats(agent.config.model, {k.value: v for k, v in stats.items() if v > 0})
    
    token_usage = agent.get_token_usage()
    logger.log_token_usage(token_usage)
    
    # Export MCP context
    mcp_context = agent.mcp_context.export_mcp_context()
    print(f"MCP context exported: {len(mcp_context)} characters")
    
    print("Comprehensive example completed successfully!")


if __name__ == "__main__":
    mcp_example()
    rich_logging_example()
    context_truncation_example()
    context_summarization_example()
    enhanced_handoff_example()
    comprehensive_example()
    
    print("\nAll examples completed!")