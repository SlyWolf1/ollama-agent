"""
Advanced example: Customer Support System with Multiple Agents
"""
from ollama_agents import Agent, tool, ThinkingMode, ModelSettings


# Define tools for different agent specializations
@tool("Search the knowledge base for solutions to customer issues")
def search_knowledge_base(query: str) -> str:
    """
    Search the knowledge base for solutions to customer issues.
    
    Args:
        query: Search query describing the issue
        
    Returns:
        str: Relevant solution or information from the knowledge base
    """
    # Simulate knowledge base search
    solutions = {
        "billing": "For billing issues, please check your payment method or contact billing@company.com",
        "technical": "For technical issues, try restarting the service or check the status page",
        "account": "For account issues, verify your credentials or reset your password"
    }
    
    for category, solution in solutions.items():
        if category in query.lower():
            return solution
    
    return "No solution found in knowledge base. Escalate to human agent."


@tool("Create a support ticket for complex issues")
def create_support_ticket(customer_id: str, issue_description: str, priority: str = "medium") -> str:
    """
    Create a support ticket for complex issues that require human intervention.
    
    Args:
        customer_id: Unique identifier for the customer
        issue_description: Detailed description of the issue
        priority: Priority level (low, medium, high)
        
    Returns:
        str: Ticket ID and confirmation message
    """
    # Simulate ticket creation
    import random
    ticket_id = f"TICK-{random.randint(1000, 9999)}"
    return f"Support ticket {ticket_id} created successfully. Priority: {priority}. A representative will contact you shortly."


def customer_support_system():
    print("=== Customer Support System Example ===")
    
    # Create specialized agents
    tech_agent = Agent(
        name="technical",
        model="qwen3-vl:2b-thinking-q8_0",
        instructions="You are a technical support specialist.",
        settings=ModelSettings(thinking_mode=ThinkingMode.NONE)
    )
    
    billing_agent = Agent(
        name="billing",
        model="qwen3-vl:2b-thinking-q8_0",
        instructions="You are a billing specialist.",
        settings=ModelSettings(thinking_mode=ThinkingMode.MEDIUM)
    )
    
    account_agent = Agent(
        name="account",
        model="qwen3-vl:2b-thinking-q8_0",
        instructions="You are an account support specialist.",
        settings=ModelSettings(thinking_mode=ThinkingMode.MEDIUM)
    )

    initial_agent = Agent(
        name="initial",
        model="qwen3-vl:2b-thinking-q8_0",
        instructions="You are the first point of contact for customer support.",
        tools=[search_knowledge_base],
        settings=ModelSettings(thinking_mode=ThinkingMode.MEDIUM),
        handoffs=[tech_agent, billing_agent, account_agent]
    )
    
    # Add handoff rules based on keywords
    initial_agent.handoff_manager.add_handoff_rule(
        lambda msg: any(word in msg.lower() for word in ["payment", "charge", "bill", "invoice"]),
        "billing",
        priority=10
    )
    
    initial_agent.handoff_manager.add_handoff_rule(
        lambda msg: any(word in msg.lower() for word in ["login", "password", "account", "profile", "access"]),
        "account",
        priority=10
    )
    
    initial_agent.handoff_manager.add_handoff_rule(
        lambda msg: any(word in msg.lower() for word in ["error", "crash", "bug", "technical", "system", "server"]),
        "technical",
        priority=10
    )
    
    # Simulate customer interactions
    customer_queries = [
        "Hi, I'm having trouble logging into my account",
        "My payment was declined and I need help", 
        "The application keeps crashing when I try to upload files",
        "How do I update my billing information?",
        "I forgot my password and can't access my account"
    ]
    
    for i, query in enumerate(customer_queries, 1):
        print(f"\n--- Customer Query {i}: {query} ---")
        
        # Process the query - this might trigger handoffs automatically
        response = initial_agent.chat(query)
        
        if "target_agent" in response:
            print(f"Handoff triggered: {response['message']}")
            print(f"Response: {response['target_agent'].messages[-1]['content'][:200]}...")
        else:
            print(f"Response: {response['content'][:200]}...")
    
    print("\nCustomer support simulation completed!")


def research_assistant_system():
    print("\n=== Research Assistant System Example ===")
    
    # Create research agents with different specializations
    search_agent = Agent(
        name="search",
        model="qwen3-vl:2b-thinking-q8_0",
        instructions="You are a research specialist. Conduct literature search and summarize findings.",
        settings=ModelSettings(thinking_mode=ThinkingMode.NONE)
    )
    
    analysis_agent = Agent(
        name="analysis",
        model="qwen3-vl:2b-thinking-q8_0",
        instructions="You are an analysis specialist. Analyze research findings and provide insights.",
        settings=ModelSettings(thinking_mode=ThinkingMode.NONE)
    )

    topic_agent = Agent(
        name="topic",
        model="qwen3-vl:2b-thinking-q8_0",
        instructions="You are a topic identification specialist. Identify the main research topic and suggest search keywords.",
        settings=ModelSettings(thinking_mode=ThinkingMode.MEDIUM),
        handoffs=[search_agent, analysis_agent]
    )
    
    # Add handoff rules
    topic_agent.handoff_manager.add_handoff_rule(
        lambda msg: "analyze" in msg.lower() or "insight" in msg.lower(),
        "analysis",
        priority=5
    )
    
    # Simulate research workflow
    research_query = "I need to research the impact of AI on healthcare"
    
    print(f"Initial query: {research_query}")
    
    # Topic agent identifies key areas
    topic_response = topic_agent.chat(research_query)
    print(f"Topic identification: {topic_response['content'][:150]}...")
    
    # Hand off to search agent
    search_request = f"Search for recent studies on: {topic_response['content'][:100]}"
    search_response = topic_agent.handoff_manager.handoff_to("search", context={"request": search_request})
    print(f"Search phase initiated: {search_response['message']}")
    
    # Search agent performs search
    search_result = search_response["target_agent"].chat("Find recent studies on AI in healthcare from 2023-2024")
    print(f"Search results summary: {search_result['content'][:150]}...")
    
    # Hand off to analysis agent
    analysis_request = f"Analyze these findings: {search_result['content'][:200]}"
    analysis_response = topic_agent.handoff_manager.handoff_to("analysis", context={"request": analysis_request})
    print(f"Analysis phase initiated: {analysis_response['message']}")
    
    # Analysis agent provides insights
    analysis_result = analysis_response["target_agent"].chat(f"What are the key insights from: {search_result['content'][:200]}")
    print(f"Analysis result: {analysis_result['content'][:200]}...")


if __name__ == "__main__":
    customer_support_system()
    research_assistant_system()
    print("\nAll advanced examples completed!")
