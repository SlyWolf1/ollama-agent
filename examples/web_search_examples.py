"""
Examples demonstrating web search capabilities
"""
from ollama_agents import Agent, enable_web_search, create_web_search_agent, SearchProvider


def basic_web_search_example():
    """Demonstrate basic web search with an agent"""
    print("=== Basic Web Search Example ===\n")
    
    # Note: You need a Brave Search API key for this to work
    # Get one free at: https://brave.com/search/api/
    
    # Create an agent
    agent = Agent(
        name="researcher",
        model="qwen2.5-coder:3b-instruct-q8_0",
        instructions="You are a helpful research assistant with web search capabilities."
    )
    
    # Enable web search (replace with your actual API key)
    enable_web_search(
        agent,
        provider=SearchProvider.BRAVE,
        api_key="YOUR_BRAVE_API_KEY",  # Replace with actual key
        max_results=5
    )
    
    print("Agent created with web search enabled")
    print("Provider: Brave Search")
    print("Max results: 5")
    print()
    
    # Example queries (these would work with actual API key)
    example_queries = [
        "What happened in tech news today?",
        "Latest developments in AI",
        "Current weather in San Francisco"
    ]
    
    print("Example queries that would use web search:")
    for i, query in enumerate(example_queries, 1):
        print(f"  {i}. {query}")
    
    print("\nNote: Set your Brave Search API key to enable actual searches")
    print()


def create_search_agent_example():
    """Demonstrate creating an agent with web search built-in"""
    print("=== Create Web Search Agent Example ===\n")
    
    # Create agent with web search in one step
    agent = create_web_search_agent(
        name="web_researcher",
        model="qwen2.5-coder:3b-instruct-q8_0",
        instructions="You are an AI assistant that can search the web for current information.",
        search_provider=SearchProvider.BRAVE,
        search_api_key="YOUR_BRAVE_API_KEY"  # Replace with actual key
    )
    
    print(f"Created agent: {agent.name}")
    print("Web search: Enabled")
    print("Ready to answer questions with current information!")
    print()


def search_with_filters_example():
    """Demonstrate web search with filters"""
    print("=== Web Search with Filters Example ===\n")
    
    from ollama_agents import SearchConfig
    
    # Create custom search configuration
    search_config = SearchConfig(
        provider=SearchProvider.BRAVE,
        api_key="YOUR_BRAVE_API_KEY",
        max_results=10,
        safe_search=True,
        time_filter="week",  # Only results from past week
        region="us"  # US region results
    )
    
    print("Search configuration:")
    print(f"  Provider: {search_config.provider.value}")
    print(f"  Max results: {search_config.max_results}")
    print(f"  Safe search: {search_config.safe_search}")
    print(f"  Time filter: {search_config.time_filter}")
    print(f"  Region: {search_config.region}")
    print()


def multi_agent_search_example():
    """Demonstrate multiple agents with different search configurations"""
    print("=== Multi-Agent Web Search Example ===\n")
    
    # News agent - searches for recent news
    news_agent = create_web_search_agent(
        name="news_agent",
        model="qwen2.5-coder:3b-instruct-q8_0",
        instructions="You are a news analyst. Search for and summarize recent news.",
        search_api_key="YOUR_BRAVE_API_KEY"
    )
    
    # Research agent - searches for detailed information
    research_agent = create_web_search_agent(
        name="research_agent",
        model="qwen2.5-coder:3b-instruct-q8_0",
        instructions="You are a research assistant. Search for comprehensive information on topics.",
        search_api_key="YOUR_BRAVE_API_KEY"
    )
    
    # Weather agent - searches for weather information
    weather_agent = create_web_search_agent(
        name="weather_agent",
        model="qwen2.5-coder:3b-instruct-q8_0",
        instructions="You are a weather assistant. Search for current weather conditions.",
        search_api_key="YOUR_BRAVE_API_KEY"
    )
    
    print("Created 3 specialized agents with web search:")
    print(f"  1. {news_agent.name} - For news analysis")
    print(f"  2. {research_agent.name} - For research")
    print(f"  3. {weather_agent.name} - For weather")
    print()


def search_providers_example():
    """Show different search provider options"""
    print("=== Search Provider Options ===\n")
    
    print("Supported search providers:")
    print("  1. Brave Search (recommended)")
    print("     - Fast and privacy-focused")
    print("     - Requires API key (get at https://brave.com/search/api/)")
    print()
    print("  2. DuckDuckGo")
    print("     - Privacy-focused")
    print("     - May require configuration")
    print()
    print("  3. SearXNG")
    print("     - Self-hosted option")
    print("     - Requires SearXNG instance")
    print()
    
    # Example configurations
    print("Example configurations:")
    print()
    print("Brave:")
    print('  enable_web_search(agent, provider=SearchProvider.BRAVE, api_key="...")')
    print()
    print("DuckDuckGo:")
    print('  enable_web_search(agent, provider=SearchProvider.DUCKDUCKGO)')
    print()
    print("SearXNG:")
    print('  enable_web_search(agent, provider=SearchProvider.SEARXNG)')
    print()


def setup_instructions():
    """Print setup instructions for web search"""
    print("=== Web Search Setup Instructions ===\n")
    
    print("To use web search with your agents:")
    print()
    print("1. Get a Brave Search API Key (Recommended)")
    print("   - Visit: https://brave.com/search/api/")
    print("   - Sign up for free tier (2,000 queries/month)")
    print("   - Copy your API key")
    print()
    print("2. Use the API key in your code:")
    print("   ```python")
    print("   from ollama_agents import Agent, enable_web_search")
    print()
    print("   agent = Agent(name='researcher', model='qwen2.5-coder:3b-instruct-q8_0')")
    print("   enable_web_search(agent, api_key='YOUR_API_KEY')")
    print()
    print("   # Now ask questions that need current information")
    print("   response = agent.chat('What happened today in tech?')")
    print("   ```")
    print()
    print("3. Models that support web search:")
    print("   - qwen2.5-coder:3b-instruct-q8_0 and later")
    print("   - Check model capabilities in Ollama docs")
    print()


if __name__ == "__main__":
    print("=" * 60)
    print("Web Search Examples for Ollama Agents")
    print("=" * 60)
    print()
    
    setup_instructions()
    basic_web_search_example()
    create_search_agent_example()
    search_with_filters_example()
    multi_agent_search_example()
    search_providers_example()
    
    print("=" * 60)
    print("For more information:")
    print("  https://docs.ollama.com/capabilities/web-search")
    print("=" * 60)
