"""
Example: Simple Collaborative Multi-Agent System

This example demonstrates three specialized agents working together:
1. File Search Agent - Uses Qdrant vector store to search documents  
2. Web Search Agent - Uses DuckDuckGo search
3. Triage Agent - Coordinates and routes queries to appropriate agents

All using local Ollama models - no API keys required!
"""
from ollama_agents import (
    Agent, tool, ModelSettings,
    TraceLevel, set_global_tracing_level, LogLevel, set_global_log_level, 
    enable_stats, get_logger, enable_logging
)
from typing import Dict, Any, List
import json


# ============================================================================
# CONFIGURATION: Enable logging if you want to see what's happening
# ============================================================================
# By default, logging is OFF for production use
# Uncomment these lines to enable detailed logging during development:

# enable_logging()  # Turn on logging
# set_global_log_level(LogLevel.DEBUG)  # Show all details
# set_global_tracing_level(TraceLevel.VERBOSE)  # Verbose tracing
# enable_stats()  # Track performance statistics

logger = get_logger()


# ============================================================================
# File Search Tools (Qdrant Vector Store)
# ============================================================================

@tool("Search documents in vector store")
def search_vector_store(query: str, limit: int = 5) -> str:
    """
    Search for relevant documents in the Qdrant vector_store collection.
    
    Args:
        query: The search query
        limit: Maximum number of results (default: 5)
        
    Returns:
        JSON string with search results
    """
    logger.info(f"🔍 Searching vector store: '{query}' (limit={limit})")
    
    try:
        from qdrant_client import QdrantClient
        
        # Connect to Qdrant
        client = QdrantClient(host="localhost", port=6333)
        
        # In production, you would generate embeddings for the query
        # For this example, we use placeholder embeddings
        results = client.search(
            collection_name="vector_store",
            query_vector=[0.0] * 384,  # Replace with actual embeddings
            limit=limit,
            with_payload=True
        )
        
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append({
                "rank": i,
                "score": result.score,
                "content": result.payload.get("content", "N/A"),
                "metadata": result.payload.get("metadata", {})
            })
        
        logger.info(f"✅ Found {len(formatted_results)} results")
        
        return json.dumps({
            "query": query,
            "results_count": len(formatted_results),
            "results": formatted_results
        }, indent=2)
        
    except ModuleNotFoundError:
        error_msg = {
            "error": "qdrant-client not installed",
            "suggestion": "Install with: pip install qdrant-client"
        }
        logger.error(f"❌ {error_msg['error']}")
        return json.dumps(error_msg)
    except Exception as e:
        error_msg = {
            "error": f"Search failed: {str(e)}",
            "suggestion": "Ensure Qdrant is running: docker run -p 6333:6333 qdrant/qdrant"
        }
        logger.error(f"❌ {error_msg['error']}")
        return json.dumps(error_msg)


@tool("Get document by ID")
def get_document_by_id(document_id: str) -> str:
    """
    Retrieve a specific document by its ID.
    
    Args:
        document_id: Document identifier
        
    Returns:
        JSON string with document content
    """
    logger.info(f"📄 Retrieving document: {document_id}")
    
    try:
        from qdrant_client import QdrantClient
        
        client = QdrantClient(host="localhost", port=6333)
        result = client.retrieve(
            collection_name="vector_store",
            ids=[document_id],
            with_payload=True
        )
        
        if result:
            doc = result[0]
            logger.info(f"✅ Document retrieved")
            return json.dumps({
                "id": document_id,
                "content": doc.payload.get("content", "N/A"),
                "metadata": doc.payload.get("metadata", {})
            }, indent=2)
        else:
            logger.warning(f"⚠️  Document not found")
            return json.dumps({"error": f"Document {document_id} not found"})
            
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        return json.dumps({"error": f"Failed to retrieve document: {str(e)}"})


@tool("List collections")
def list_collections() -> str:
    """List all available Qdrant collections."""
    logger.info("📋 Listing collections")
    
    try:
        from qdrant_client import QdrantClient
        
        client = QdrantClient(host="localhost", port=6333)
        collections = client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        logger.info(f"✅ Found {len(collection_names)} collections")
        
        return json.dumps({
            "collections": collection_names,
            "count": len(collection_names)
        }, indent=2)
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        return json.dumps({"error": f"Failed to list collections: {str(e)}"})


# ============================================================================
# Web Search Tools (DuckDuckGo)
# ============================================================================

@tool("Search the web")
def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo.
    
    Args:
        query: Search query
        max_results: Maximum results (default: 5)
        
    Returns:
        JSON formatted search results
    """
    logger.info(f"🌐 Web searching: '{query}'")
    
    try:
        from ollama_agents.ddg_search import search_duckduckgo_sync
        
        results = search_duckduckgo_sync(query, max_results)
        logger.info(f"✅ Web search completed")
        return results
        
    except Exception as e:
        error_msg = {
            "error": f"Web search failed: {str(e)}",
            "suggestion": "Install Playwright: pip install playwright && playwright install chromium"
        }
        logger.error(f"❌ {error_msg['error']}")
        return json.dumps(error_msg)


# ============================================================================
# Create Specialized Agents
# ============================================================================

def create_file_search_agent() -> Agent:
    """Create file search agent with Qdrant vector store access."""
    logger.info("🔧 Creating file search agent")
    
    agent = Agent(
        name="file_search_agent",
        model="qwen2.5-coder:3b-instruct-q8_0",
        instructions="""You are a document search specialist with access to a Qdrant vector database.

Your job:
- Search the 'vector_store' collection for relevant documents
- Retrieve specific documents by ID
- Provide accurate information from the document store
- Always cite document IDs when providing information

When searching:
1. Use search_vector_store to find relevant documents
2. Analyze results and extract key information
3. Cite sources (document IDs)
4. If results are insufficient, try rephrasing the query

Available tools: search_vector_store, get_document_by_id, list_collections""",
        tools=[search_vector_store, get_document_by_id, list_collections],
        temperature=0.3,
        max_tokens=1000,
        timeout=60,
        enable_tracing=False,  # Disabled by default
        trace_level=TraceLevel.OFF
    )
    
    logger.info(f"✅ Created: {agent.name}")
    return agent


def create_web_search_agent() -> Agent:
    """Create web search agent with DuckDuckGo access."""
    logger.info("🔧 Creating web search agent")
    
    agent = Agent(
        name="web_search_agent",
        model="qwen2.5-coder:3b-instruct-q8_0",
        instructions="""You are a web search specialist using DuckDuckGo.

Your job:
- Search the web for current information and news
- Provide up-to-date answers requiring recent data
- Verify information from multiple sources when possible
- Always cite sources and provide links

When searching:
1. Use web_search to find relevant information
2. Summarize key findings clearly
3. Mention sources (URLs)
4. Indicate timeliness of information

Handle queries about:
- Current events and news
- Real-time data (weather, stocks, etc.)
- Recent developments
- Information not in static document stores

Use web_search tool to get results, then synthesize a helpful response.""",
        tools=[web_search],
        temperature=0.4,
        max_tokens=1000,
        timeout=60,
        enable_tracing=False,  # Disabled by default
        trace_level=TraceLevel.OFF
    )
    
    logger.info(f"✅ Created: {agent.name}")
    return agent


def create_triage_agent(file_agent: Agent, web_agent: Agent) -> Agent:
    """Create triage agent to coordinate between specialized agents."""
    logger.info("🔧 Creating triage agent")
    
    @tool("Route to file search")
    def route_to_file_search(query: str) -> str:
        """
        Route query to file search agent for document-based information.
        
        Args:
            query: Query to send to file search agent
            
        Returns:
            Complete response from file search agent
        """
        logger.info(f"📂 Routing to file search: '{query}'")
        response = file_agent.chat(query)
        content = response.get('content', 'No response')
        logger.info(f"✅ File search responded ({len(content)} chars)")
        logger.debug(f"Response preview: {content[:200]}...")
        return content
    
    @tool("Route to web search")
    def route_to_web_search(query: str) -> str:
        """
        Route query to web search agent for current web information.
        
        Args:
            query: Query to send to web search agent
            
        Returns:
            Complete response from web search agent
        """
        logger.info(f"🌐 Routing to web search: '{query}'")
        response = web_agent.chat(query)
        content = response.get('content', 'No response')
        logger.info(f"✅ Web search responded ({len(content)} chars)")
        logger.debug(f"Response preview: {content[:200]}...")
        return content
    
    agent = Agent(
        name="triage_agent",
        model="qwen2.5-coder:3b-instruct-q8_0",
        instructions="""You are an intelligent triage coordinator managing two specialized agents:

1. FILE SEARCH AGENT - Searches documents in Qdrant vector_store
   Use for: Static documents, knowledge base, stored info, company docs

2. WEB SEARCH AGENT - Searches the internet
   Use for: Current events, real-time data, news, weather, stocks

Your workflow:
1. Analyze the user's query
2. Decide which agent is best suited
3. Call the appropriate routing tool (route_to_file_search OR route_to_web_search)
4. The tool will return the specialized agent's complete answer
5. Present that answer directly to the user - don't call tools again!

Decision guidelines:
- CURRENT/RECENT info → use route_to_web_search
- STORED/HISTORICAL docs → use route_to_file_search  
- BOTH needed → use both tools, combine results
- If unsure → try File Search first, then Web if needed

CRITICAL: After calling a routing tool, you receive the FINAL ANSWER.
Present it to the user. Don't route again!

Example:
User: "Find company policy on vacation"
You think: Internal docs → File Search
You call: route_to_file_search("company vacation policy")
Tool returns: "According to our HR policy document, employees receive..."
You present: "According to our HR policy document, employees receive..."
Done! Don't call any more tools.""",
        tools=[route_to_file_search, route_to_web_search],
        temperature=0.2,
        max_tokens=2000,
        timeout=120,
        enable_tracing=False,  # Disabled by default
        trace_level=TraceLevel.OFF
    )
    
    logger.info(f"✅ Created: {agent.name}")
    return agent


# ============================================================================
# Main Example
# ============================================================================

def main():
    """Run the collaborative multi-agent example."""
    print("=" * 80)
    print("COLLABORATIVE MULTI-AGENT SYSTEM")
    print("=" * 80)
    print("\nFeatures:")
    print("  ✓ File Search Agent (Qdrant vector store)")
    print("  ✓ Web Search Agent (DuckDuckGo)")
    print("  ✓ Triage Agent (Smart routing)")
    print("  ✓ No API keys required!")
    print("\n" + "=" * 80)
    print()
    
    # Create agents
    logger.info("Creating agents...")
    print("🔧 Creating agents...")
    
    file_agent = create_file_search_agent()
    web_agent = create_web_search_agent()
    triage_agent = create_triage_agent(file_agent, web_agent)
    
    print("   ✓ All agents ready")
    print()
    
    # Example queries
    print("📋 Example Queries:")
    print("  1. 'Search our docs for API authentication info'")
    print("  2. 'What are the latest AI news this week?'")
    print("  3. 'What's the weather like today?'")
    print()
    print("=" * 80)
    print()
    
    # Setup instructions
    print("⚙️  SETUP REQUIREMENTS:")
    print()
    print("1. For FILE SEARCH - Start Qdrant:")
    print("   docker run -p 6333:6333 qdrant/qdrant")
    print()
    print("2. For WEB SEARCH - Install Playwright:")
    print("   pip install playwright && playwright install chromium")
    print()
    print("=" * 80)
    print()
    
    # Interactive mode
    print("🚀 INTERACTIVE MODE")
    print("   Type your query (or 'exit' to quit)")
    print("=" * 80)
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
            
            print(f"\n🤖 Response:")
            print("-" * 80)
            print(response['content'])
            print("-" * 80)
            
            logger.info("Query completed")
            
        except KeyboardInterrupt:
            logger.info("User interrupted")
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            print(f"\n❌ Error: {e}")
    
    # Print statistics if enabled
    try:
        from ollama_agents import get_stats_tracker
        stats = get_stats_tracker()
        
        print("\n" + "=" * 80)
        print("📊 SESSION STATISTICS")
        print("=" * 80)
        
        for agent_name in [file_agent.name, web_agent.name, triage_agent.name]:
            agent_stats = stats.get_agent_stats(agent_name)
            if agent_stats:
                print(f"\n{agent_name}:")
                for stat_type, value in agent_stats.items():
                    print(f"  {stat_type.name}: {value}")
        
        print("\n" + "=" * 80)
    except:
        pass  # Stats not enabled
    
    logger.info("Example completed")


if __name__ == "__main__":
    # To enable logging, uncomment these lines at the top of the file:
    # enable_logging()
    # set_global_log_level(LogLevel.INFO)  # or LogLevel.DEBUG for more detail
    # enable_stats()
    
    main()
