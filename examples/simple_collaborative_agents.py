"""
Simple Example: Three Agents Working Together
- File Search Agent: Searches Qdrant vector store
- Web Search Agent: Searches the web with DuckDuckGo  
- Triage Agent: Coordinates between the two agents

This example demonstrates agent handoffs and tool calling.
"""
from ollama_agents import (
    Agent, tool, ModelSettings,
    enable_logging, set_global_log_level, LogLevel,
    enable_stats, get_stats_tracker, get_logger
)
from typing import Dict, Any
import json


# ============================================================================
# STEP 1: Enable Logging (Optional - disabled by default)
# ============================================================================

# Uncomment to see detailed logs:
enable_logging()
set_global_log_level(LogLevel.DEBUG)
enable_stats()

logger = get_logger()


# ============================================================================
# STEP 2: Define Tools for Each Agent
# ============================================================================

# File Search Tools (Qdrant integration)
@tool("Search documents in Qdrant vector store")
def search_vector_store(query: str, limit: int = 5) -> str:
    """Search for relevant documents in the vector_store collection."""
    logger.info(f"🔍 Searching vector store: '{query}'")
    
    try:
        from qdrant_client import QdrantClient
        
        client = QdrantClient(host="localhost", port=6333)
        
        # In production, you'd use proper embeddings
        # This is a simplified example
        results = client.search(
            collection_name="vector_store",
            query_vector=[0.0] * 384,  # Replace with actual embedding
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
        
        return json.dumps({
            "query": query,
            "results_count": len(formatted_results),
            "results": formatted_results
        }, indent=2)
        
    except ModuleNotFoundError:
        return json.dumps({
            "error": "qdrant-client not installed",
            "instruction": "Install with: pip install qdrant-client"
        })
    except Exception as e:
        return json.dumps({
            "error": f"Search failed: {str(e)}",
            "instruction": "Ensure Qdrant is running: docker run -p 6333:6333 qdrant/qdrant"
        })


@tool("Get document by ID")
def get_document_by_id(document_id: str) -> str:
    """Retrieve a specific document by its ID."""
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
            return json.dumps({
                "id": document_id,
                "content": doc.payload.get("content", "N/A"),
                "metadata": doc.payload.get("metadata", {})
            }, indent=2)
        else:
            return json.dumps({"error": f"Document {document_id} not found"})
    except Exception as e:
        return json.dumps({"error": f"Failed to retrieve document: {str(e)}"})


# Web Search Tool (DuckDuckGo)
@tool("Search the web with DuckDuckGo")
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web using DuckDuckGo (no API keys needed)."""
    logger.info(f"🔍 Web search: '{query}'")
    
    try:
        from ollama_agents.ddg_search import search_duckduckgo_sync
        results = search_duckduckgo_sync(query, max_results)
        logger.info(f"✅ Web search completed")
        return results
    except ModuleNotFoundError as e:
        return json.dumps({
            "error": f"Missing dependency: {str(e)}",
            "instruction": "Install with: pip install playwright && playwright install chromium"
        })
    except Exception as e:
        logger.error(f"❌ Web search failed: {e}")
        return json.dumps({
            "error": f"Search failed: {str(e)}"
        })


# ============================================================================
# STEP 3: Create Specialized Agents
# ============================================================================

def create_file_search_agent() -> Agent:
    """Create an agent that searches document stores."""
    return Agent(
        name="file_search_agent",
        model="qwen2.5-coder:3b-instruct-q8_0",
        instructions="""You are a file search specialist.
        
Your job:
- Search the vector_store collection for relevant documents
- Retrieve specific documents by ID when requested
- Provide accurate information from the document store

When you get a query, use search_vector_store to find relevant documents.
Always provide clear, helpful responses based on what you find.""",
        tools=[search_vector_store, get_document_by_id],
        settings=ModelSettings(
            temperature=0.3,
            max_tokens=1000
        ),
        timeout=60
    )


def create_web_search_agent() -> Agent:
    """Create an agent that searches the web."""
    return Agent(
        name="web_search_agent",
        model="qwen2.5-coder:3b-instruct-q8_0",
        instructions="""You are a web search specialist.

Your job:
- Search the web for current information using DuckDuckGo
- Provide up-to-date answers with sources
- Cite URLs when providing information

When you get a query, use web_search to find relevant information.
Always summarize findings clearly and cite your sources.""",
        tools=[web_search],
        settings=ModelSettings(
            temperature=0.4,
            max_tokens=1000
        ),
        timeout=60
    )


def create_triage_agent(file_agent: Agent, web_agent: Agent) -> Agent:
    """Create a triage agent that coordinates the other agents."""
    
    @tool("Route query to file search agent")
    def route_to_file_search(query: str) -> str:
        """Route a query to the file search agent for document-based information."""
        logger.info(f"📂 Routing to file search agent: '{query}'")
        response = file_agent.chat(query)
        content = response.get('content', 'No response from file search agent')
        logger.info(f"✅ File search agent responded")
        return content
    
    @tool("Route query to web search agent")
    def route_to_web_search(query: str) -> str:
        """Route a query to the web search agent for current web information."""
        logger.info(f"🌐 Routing to web search agent: '{query}'")
        response = web_agent.chat(query)
        content = response.get('content', 'No response from web search agent')
        logger.info(f"✅ Web search agent responded")
        return content
    
    return Agent(
        name="triage_agent",
        model="qwen2.5-coder:3b-instruct-q8_0",
        instructions="""You are a smart coordinator managing two specialized agents:

1. FILE SEARCH AGENT - Searches documents in vector_store
   Use for: Company docs, stored information, internal knowledge base

2. WEB SEARCH AGENT - Searches the internet
   Use for: Current events, real-time data, recent news, weather

Your job:
1. Analyze the user's query
2. Decide which agent can best answer it
3. Route the query using route_to_file_search or route_to_web_search
4. IMPORTANT: After calling a routing tool, YOU MUST present the agent's response to the user

Decision rules:
- Current/recent information → web_search_agent
- Stored/historical documents → file_search_agent
- Both needed → use both agents and combine results

CRITICAL: When you receive a response from a routing tool, that IS the answer.
Present it clearly to the user. Don't ask to route again - the routing already happened!""",
        tools=[route_to_file_search, route_to_web_search],
        settings=ModelSettings(
            temperature=0.2,
            max_tokens=2000
        ),
        timeout=120
    )


# ============================================================================
# STEP 4: Run Interactive Demo
# ============================================================================

def main():
    """Run the collaborative agents demo."""
    print("=" * 80)
    print("COLLABORATIVE AGENTS DEMO")
    print("=" * 80)
    print("\nThree agents working together:")
    print("  1. File Search Agent - Searches Qdrant vector store")
    print("  2. Web Search Agent - Searches the web with DuckDuckGo")
    print("  3. Triage Agent - Routes queries to the right agent")
    print("\n" + "=" * 80)
    print("\n📝 NOTE: Logging is DISABLED by default.")
    print("   To enable detailed logs, uncomment lines 20-22 in the code.")
    print("\n" + "=" * 80 + "\n")
    
    # Create agents
    print("🔧 Creating agents...")
    file_agent = create_file_search_agent()
    print(f"   ✓ {file_agent.name}")
    
    web_agent = create_web_search_agent()
    print(f"   ✓ {web_agent.name}")
    
    triage_agent = create_triage_agent(file_agent, web_agent)
    print(f"   ✓ {triage_agent.name}")
    print()
    
    # Interactive mode
    print("🚀 Starting interactive mode...")
    print("   Type your query and the triage agent will route it appropriately.")
    print("   Type 'exit' or 'quit' to stop.\n")
    
    while True:
        try:
            query = input("🤔 Your query: ").strip()
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not query:
                continue
            
            print(f"\n🔄 Processing with triage agent...\n")
            response = triage_agent.chat(query)
            print(f"🤖 Response:\n{response['content']}\n")
            print("-" * 80 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
    
    # Show statistics if enabled
    if get_stats_tracker()._enabled:
        print("\n" + "=" * 80)
        print("📊 SESSION STATISTICS")
        print("=" * 80)
        for agent_name in [file_agent.name, web_agent.name, triage_agent.name]:
            agent_stats = get_stats_tracker().get_agent_stats(agent_name)
            if agent_stats:
                print(f"\n{agent_name}:")
                for stat_type, value in agent_stats.items():
                    print(f"  {stat_type.name}: {value}")
        print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
