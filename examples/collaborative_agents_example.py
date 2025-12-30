"""
Example: Collaborative Multi-Agent System with File Search, Web Search, and Triage

This example demonstrates three specialized agents working together:
1. File Search Agent - Uses Qdrant vector store to search documents
2. Web Search Agent - Uses Ollama's native web search (no API keys needed!)
3. Triage Agent - Coordinates and routes queries to appropriate agents
"""
from ollama_agents import (
    Agent, tool, ThinkingMode, ModelSettings,
    TraceLevel, set_global_tracing_level, LogLevel, set_global_log_level, 
    enable_stats, get_logger
)
from typing import Dict, Any, List
import json


# ============================================================================
# Configure Logging and Tracing
# ============================================================================

# Enable comprehensive logging
set_global_log_level(LogLevel.DEBUG)  # Show all log messages
set_global_tracing_level(TraceLevel.VERBOSE)  # Detailed tracing
enable_stats()  # Track statistics

# Get logger instance
logger = get_logger()
logger.info("=" * 80)
logger.info("COLLABORATIVE AGENTS EXAMPLE - STARTING")
logger.info("=" * 80)


# ============================================================================
# File Search Tools (Using Qdrant Vector Store)
# ============================================================================

@tool("Search documents in Qdrant vector store")
def search_vector_store(query: str, limit: int = 5) -> str:
    """
    Search for relevant documents in the Qdrant vector_store collection.
    
    Args:
        query: The search query to find relevant documents
        limit: Maximum number of results to return (default: 5)
        
    Returns:
        str: JSON string containing search results with document content and metadata
    """
    logger.info(f"🔍 Searching vector store: query='{query}', limit={limit}")
    
    try:
        # Import qdrant_client
        from qdrant_client import QdrantClient
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        logger.debug("Connecting to Qdrant at localhost:6333")
        # Connect to Qdrant (adjust host/port as needed)
        client = QdrantClient(host="localhost", port=6333)
        
        logger.debug(f"Searching collection 'vector_store' for: {query}")
        # Search the vector_store collection
        # Note: This is a simplified example. In production, you'd generate embeddings
        # for the query using the same model that created the collection embeddings
        results = client.search(
            collection_name="vector_store",
            query_vector=[0.0] * 384,  # Placeholder - replace with actual embedding
            limit=limit,
            with_payload=True
        )
        
        logger.info(f"Found {len(results)} results from vector store")
        
        # Format results
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append({
                "rank": i,
                "score": result.score,
                "content": result.payload.get("content", "N/A"),
                "metadata": result.payload.get("metadata", {})
            })
        
        return json.dumps({
            "query": query,
            "results_count": len(formatted_results),
            "results": formatted_results
        }, indent=2)
        
    except ModuleNotFoundError as e:
        logger.error(f"❌ Missing dependency: {str(e)}")
        return json.dumps({
            "error": "qdrant-client not installed",
            "suggestion": "Install with: pip install qdrant-client"
        })
    except Exception as e:
        logger.error(f"❌ Error searching vector store: {str(e)}")
        return json.dumps({
            "error": f"Failed to search vector store: {str(e)}",
            "suggestion": "Ensure Qdrant is running (docker run -p 6333:6333 qdrant/qdrant) and vector_store collection exists"
        })


@tool("Get document by ID from vector store")
def get_document_by_id(document_id: str) -> str:
    """
    Retrieve a specific document from the vector_store by its ID.
    
    Args:
        document_id: Unique identifier of the document
        
    Returns:
        str: JSON string containing document content and metadata
    """
    logger.info(f"📄 Retrieving document by ID: {document_id}")
    
    try:
        from qdrant_client import QdrantClient
        
        client = QdrantClient(host="localhost", port=6333)
        
        logger.debug(f"Retrieving document {document_id} from vector_store")
        # Retrieve the document
        result = client.retrieve(
            collection_name="vector_store",
            ids=[document_id],
            with_payload=True
        )
        
        if result:
            doc = result[0]
            logger.info(f"✅ Document {document_id} retrieved successfully")
            return json.dumps({
                "id": document_id,
                "content": doc.payload.get("content", "N/A"),
                "metadata": doc.payload.get("metadata", {})
            }, indent=2)
        else:
            logger.warning(f"⚠️  Document {document_id} not found")
            return json.dumps({"error": f"Document {document_id} not found"})
            
    except Exception as e:
        logger.error(f"❌ Error retrieving document {document_id}: {str(e)}")
        return json.dumps({"error": f"Failed to retrieve document: {str(e)}"})


@tool("List available collections in Qdrant")
def list_collections() -> str:
    """
    List all available collections in the Qdrant vector database.
    
    Returns:
        str: JSON string containing list of collection names
    """
    logger.info("📋 Listing all Qdrant collections")
    
    try:
        from qdrant_client import QdrantClient
        
        client = QdrantClient(host="localhost", port=6333)
        collections = client.get_collections()
        
        collection_names = [col.name for col in collections.collections]
        
        logger.info(f"✅ Found {len(collection_names)} collections: {collection_names}")
        
        return json.dumps({
            "collections": collection_names,
            "count": len(collection_names)
        }, indent=2)
        
    except Exception as e:
        logger.error(f"❌ Error listing collections: {str(e)}")
        return json.dumps({"error": f"Failed to list collections: {str(e)}"})


# ============================================================================
# Create Specialized Agents
# ============================================================================

def create_file_search_agent() -> Agent:
    """Create an agent specialized in searching documents using Qdrant vector store."""
    logger.info("🔧 Creating file search agent...")
    
    agent = Agent(
        name="file_search_agent",
        model="qwen2.5-coder:3b-instruct-q8_0",
        instructions="""You are a specialized file search assistant with access to a Qdrant vector database.
        
Your responsibilities:
- Search the 'vector_store' collection for relevant documents based on user queries
- Retrieve specific documents by ID when requested
- Provide accurate and relevant information from the document store
- Explain search results clearly and concisely

When searching, always:
1. Use the search_vector_store tool to find relevant documents
2. Analyze the results and extract the most relevant information
3. Cite document IDs when providing information
4. If results are not satisfactory, try rephrasing the query

Available tools:
- search_vector_store: Search documents by query
- get_document_by_id: Retrieve specific documents
- list_collections: Check available collections""",
        tools=[search_vector_store, get_document_by_id, list_collections],
        settings=ModelSettings(
            # thinking_mode=ThinkingMode.MEDIUM,
            temperature=0.3,
            max_tokens=1000
        ),
        timeout=60,
        enable_tracing=True,
        trace_level=TraceLevel.VERBOSE
    )
    
    logger.info(f"✅ File search agent created: {agent.name}")
    logger.debug(f"   Model: {agent.model}")
    logger.debug(f"   Tools: {len(agent.tools)}")
    logger.debug(f"   Tracing: {agent.enable_tracing}")
    
    return agent


def create_web_search_agent(model: str = None) -> Agent:
    """
    Create an agent specialized in web searching using DuckDuckGo + Playwright.
    
    No API keys needed!
    """
    logger.info("🔧 Creating web search agent with DuckDuckGo...")
    
    # Use a model that supports web search or default to qwen
    if model is None:
        model = "qwen2.5-coder:3b-instruct-q8_0"
    
    # Import and create the DuckDuckGo search tool
    from ollama_agents.ddg_search import search_duckduckgo_sync
    
    @tool("Search the web with DuckDuckGo")
    def web_search(query: str, max_results: int = 5) -> str:
        """
        Search the web using DuckDuckGo.
        
        Args:
            query: Search query
            max_results: Maximum number of results (default 5)
            
        Returns:
            JSON formatted search results with titles, URLs, and snippets
        """
        logger.info(f"🔍 Searching DuckDuckGo: '{query}'")
        try:
            results = search_duckduckgo_sync(query, max_results)
            logger.info(f"✅ Found search results")
            return results
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return json.dumps({
                "error": f"Search failed: {str(e)}",
                "suggestion": "Make sure Playwright is installed: pip install playwright && playwright install chromium"
            })
    
    agent = Agent(
        name="web_search_agent",
        model=model,
        instructions="""You are a specialized web search assistant with access to DuckDuckGo search.

Your responsibilities:
- Search the web for current information, news, and real-time data
- Provide up-to-date answers to questions requiring recent information
- Verify information from multiple sources when possible
- Cite sources and provide links when available

When searching, always:
1. Use the web_search tool to find recent and relevant information
2. Summarize key findings clearly from the search results
3. Mention the sources (URLs) of your information
4. Indicate the timeliness of the information

You should handle queries about:
- Current events and news
- Real-time data (weather, stock prices, etc.)
- Recent developments in any field
- Information not available in static document stores

Use the web_search tool to get actual search results, then synthesize them into a helpful response.""",
        tools=[web_search],
        settings=ModelSettings(
            temperature=0.4,
            max_tokens=1000
        ),
        timeout=60,
        enable_tracing=True,
        trace_level=TraceLevel.VERBOSE
    )
    
    logger.info(f"✅ Web search agent created: {agent.name}")
    logger.info(f"   Using DuckDuckGo + Playwright")
    logger.debug(f"   Model: {agent.model}")
    logger.debug(f"   Tracing: {agent.enable_tracing}")
    
    return agent
    logger.debug(f"   Model: {agent.model}")
    logger.debug(f"   API Key provided: {bool(api_key)}")
    logger.debug(f"   Tracing: {agent.enable_tracing}")
    
    return agent


def create_triage_agent(file_agent: Agent, web_agent: Agent) -> Agent:
    """Create a triage agent that coordinates between file and web search agents."""
    logger.info("🔧 Creating triage agent...")
    
    @tool("Route query to file search agent")
    def route_to_file_search(query: str) -> str:
        """
        Route a query to the file search agent for document-based information.
        
        Args:
            query: The query to send to the file search agent
            
        Returns:
            str: Full response from the file search agent including any errors or explanations
        """
        logger.info(f"📂 Routing to file search agent: '{query}'")
        response = file_agent.chat(query)
        content = response.get('content', 'No response from file search agent')
        logger.info(f"✅ File search agent responded ({len(content)} chars)")
        logger.debug(f"Full response: {content}")
        
        # Return the complete response so triage agent can show it
        return content
    
    @tool("Route query to web search agent")
    def route_to_web_search(query: str) -> str:
        """
        Route a query to the web search agent for current web information.
        
        Args:
            query: The query to send to the web search agent
            
        Returns:
            str: Full response from the web search agent including any errors or explanations
        """
        logger.info(f"🌐 Routing to web search agent: '{query}'")
        response = web_agent.chat(query)
        content = response.get('content', 'No response from web search agent')
        logger.info(f"✅ Web search agent responded ({len(content)} chars)")
        logger.debug(f"Full response: {content}")
        
        # Return the complete response so triage agent can show it
        return content
    
    agent = Agent(
        name="triage_agent",
        model="qwen2.5-coder:3b-instruct-q8_0",
        instructions="""You are an intelligent triage coordinator managing two specialized agents:

1. FILE SEARCH AGENT - Searches documents in Qdrant vector_store
   Use for: Static documents, internal knowledge base, stored information, company docs

2. WEB SEARCH AGENT - Searches the internet for current information
   Use for: Current events, real-time data, recent news, trending topics, weather, stocks

Your responsibilities:
- Analyze incoming user queries
- Determine which agent(s) can best answer the query
- Route queries to the appropriate specialized agent
- Show the FULL response from the specialized agent to the user
- If the agent returns an error or says something is unavailable, SHOW THAT MESSAGE
- Synthesize responses from multiple agents if needed

Decision making guidelines:
- If query needs CURRENT/RECENT information → use Web Search Agent
- If query needs STORED/HISTORICAL documents → use File Search Agent
- If query needs BOTH sources → use both agents and combine results
- If unsure → try File Search first, then Web Search if needed

IMPORTANT: 
- Always show the complete response from the specialized agent
- If an agent says "qdrant-client not installed" or any error, relay that message
- Don't hide error messages - they help the user understand what's needed
- Present the agent's response clearly, even if it's an error or limitation

Format your response like:
"I routed your query to [Agent Name]. Here's their response:

[Full agent response here, including errors or explanations]"

Always be transparent about what happened.""",
        tools=[route_to_file_search, route_to_web_search],
        settings=ModelSettings(
            temperature=0.2,
            max_tokens=2000
        ),
        timeout=120,
        enable_tracing=True,
        trace_level=TraceLevel.VERBOSE
    )
    
    logger.info(f"✅ Triage agent created: {agent.name}")
    logger.debug(f"   Model: {agent.model}")
    logger.debug(f"   Tools: {len(agent.tools)}")
    logger.debug(f"   Thinking mode: {agent.settings.thinking_mode}")
    logger.debug(f"   Tracing: {agent.enable_tracing}")
    
    return agent


# ============================================================================
# Main Example
# ============================================================================

def run_collaborative_example():
    """
    Run the collaborative multi-agent example.
    
    Uses Ollama's native web search - no API keys needed!
    """
    logger.info("=" * 80)
    logger.info("STARTING COLLABORATIVE MULTI-AGENT SYSTEM")
    logger.info("=" * 80)
    
    print("=" * 80)
    print("COLLABORATIVE MULTI-AGENT SYSTEM")
    print("=" * 80)
    print()
    
    # Create specialized agents
    logger.info("Creating specialized agents...")
    print("🔧 Creating specialized agents...")
    
    file_search_agent = create_file_search_agent()
    print(f"   ✓ {file_search_agent.name} - Qdrant vector store search")
    
    web_search_agent = create_web_search_agent()
    print(f"   ✓ {web_search_agent.name} - Ollama native web search")
    
    triage_agent = create_triage_agent(file_search_agent, web_search_agent)
    print(f"   ✓ {triage_agent.name} - Query coordination and routing")
    print()
    
    logger.info("All agents created successfully")
    logger.info(f"  - File search agent: {file_search_agent.name}")
    logger.info(f"  - Web search agent: {web_search_agent.name}")
    logger.info(f"  - Triage agent: {triage_agent.name}")
    
    # Example queries
    example_queries = [
        # File search query
        {
            "query": "Search our document store for information about API authentication",
            "expected_agent": "file_search_agent"
        },
        # Web search query
        {
            "query": "What are the latest developments in AI this week?",
            "expected_agent": "web_search_agent"
        },
        # Mixed query
        {
            "query": "Compare our internal security policies with current industry best practices",
            "expected_agent": "both agents"
        }
    ]
    
    logger.info(f"Prepared {len(example_queries)} example queries")
    print("📋 Example queries to demonstrate agent collaboration:")
    print()
    
    for i, example in enumerate(example_queries, 1):
        logger.debug(f"Example query {i}: {example['query']}")
        print(f"Query {i}: {example['query']}")
        print(f"Expected routing: {example['expected_agent']}")
        print("-" * 80)
        
        # In production, you would actually run this:
        # logger.info(f"Executing query {i}...")
        # response = triage_agent.chat(example['query'])
        # logger.info(f"Response received: {len(response['content'])} chars")
        # print(f"Response: {response['content']}")
        
        print()
    
    print("=" * 80)
    print("USAGE INSTRUCTIONS")
    print("=" * 80)
    print()
    print("To use this system:")
    print()
    print("1. Ensure Qdrant is running (for file search):")
    print("   docker run -p 6333:6333 qdrant/qdrant")
    print()
    print("2. Create a 'vector_store' collection in Qdrant with your documents")
    print()
    print("3. Web search works out of the box using Ollama's native search!")
    print("   No API keys needed!")
    print()
    print("4. Run queries through the triage agent:")
    print()
    print("   response = triage_agent.chat('Your query here')")
    print("   print(response['content'])")
    print()
    print("=" * 80)
    print()
    
    # Interactive mode (optional)
    print("💡 Want to try it interactively? (requires Qdrant running)")
    print("   Uncomment the interactive section below in the code")
    print()
    
    # """
    # Uncomment for interactive mode:
    
    print("🚀 Starting interactive mode...")
    print("   Type 'exit' or 'quit' to stop")
    print()
    
    while True:
        try:
            user_query = input("\n🤔 Your query: ").strip()
            
            if user_query.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not user_query:
                continue
            
            logger.info(f"User query: {user_query}")
            print(f"\n🔄 Processing with triage agent...")
            response = triage_agent.chat(user_query)
            print(f"\n🤖 Response:\n{response['content']}")
            logger.info("Query completed successfully")
            
        except KeyboardInterrupt:
            logger.info("User interrupted - shutting down")
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            print(f"\n❌ Error: {e}")
    
    # Print statistics summary
    from ollama_agents import get_stats_tracker
    stats = get_stats_tracker()
    
    logger.info("=" * 80)
    logger.info("SESSION STATISTICS")
    logger.info("=" * 80)
    
    print("\n" + "=" * 80)
    print("📊 SESSION STATISTICS")
    print("=" * 80)
    
    # Get stats for each agent
    for agent_name in [file_search_agent.name, web_search_agent.name, triage_agent.name]:
        agent_stats = stats.get_agent_stats(agent_name)
        if agent_stats:
            print(f"\n{agent_name}:")
            logger.info(f"{agent_name} stats: {agent_stats}")
            for stat_type, value in agent_stats.items():
                print(f"  {stat_type.name}: {value}")
    
    print("\n" + "=" * 80)
    logger.info("Example completed")
    # """


def test_file_search_agent():
    """Test the file search agent independently."""
    print("=" * 80)
    print("TESTING FILE SEARCH AGENT")
    print("=" * 80)
    print()
    
    agent = create_file_search_agent()
    
    test_queries = [
        "List all available collections",
        "Search for documents about machine learning",
        "Find documents related to API documentation"
    ]
    
    for query in test_queries:
        print(f"Query: {query}")
        print("-" * 80)
        # Uncomment to actually run:
        # response = agent.chat(query)
        # print(f"Response: {response['content']}")
        print()


def test_web_search_agent():
    """Test the web search agent independently."""
    print("=" * 80)
    print("TESTING WEB SEARCH AGENT (Ollama Native)")
    print("=" * 80)
    print()
    
    agent = create_web_search_agent()
    
    test_queries = [
        "What is the current weather?",
        "Latest tech news today",
        "Recent AI breakthroughs"
    ]
    
    for query in test_queries:
        print(f"Query: {query}")
        print("-" * 80)
        if brave_api_key:
            # Uncomment to actually run:
            # response = agent.chat(query)
            # print(f"Response: {response['content']}")
            pass
        else:
            print("⚠️  Skipping - no API key provided")
        print()


if __name__ == "__main__":
    # Run the main example with Ollama native web search
    # No API keys needed!
    
    run_collaborative_example()
    
    # Optionally test individual agents
    # test_file_search_agent()
    # test_web_search_agent()
