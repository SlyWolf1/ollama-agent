#!/usr/bin/env python3
"""
Quick Demo: Collaborative Multi-Agent System

This script demonstrates the 3-agent collaborative system with minimal setup.
Run this to see how the agents work together!
"""

from collaborative_agents_example import (
    create_file_search_agent,
    create_web_search_agent,
    create_triage_agent
)


def main():
    print("=" * 80)
    print("🤖 COLLABORATIVE AGENTS DEMO")
    print("=" * 80)
    print()
    
    # Step 1: Create the agents
    print("Step 1: Creating specialized agents...")
    print()
    
    file_agent = create_file_search_agent()
    print(f"✓ Created {file_agent.name}")
    print(f"  Purpose: Search Qdrant vector_store collection")
    print(f"  Tools: search_vector_store, get_document_by_id, list_collections")
    print()
    
    # Note: Replace None with your Brave API key to enable web search
    BRAVE_API_KEY = None  # or "your-brave-api-key-here"
    web_agent = create_web_search_agent(api_key=BRAVE_API_KEY)
    print(f"✓ Created {web_agent.name}")
    print(f"  Purpose: Search the web for current information")
    print(f"  Provider: Brave Search")
    print()
    
    triage_agent = create_triage_agent(file_agent, web_agent)
    print(f"✓ Created {triage_agent.name}")
    print(f"  Purpose: Coordinate and route queries")
    print(f"  Intelligence: HIGH thinking mode")
    print()
    
    # Step 2: Explain the workflow
    print("=" * 80)
    print("📋 HOW IT WORKS")
    print("=" * 80)
    print()
    print("User Query → Triage Agent → Routes to appropriate specialist:")
    print()
    print("  📂 File Search Agent")
    print("     ├─ Searches Qdrant vector_store collection")
    print("     ├─ Handles: internal docs, stored information, knowledge base")
    print("     └─ Tools: search_vector_store, get_document_by_id")
    print()
    print("  🌐 Web Search Agent")
    print("     ├─ Searches the internet via Brave Search API")
    print("     ├─ Handles: current events, real-time data, news")
    print("     └─ Requires: Brave Search API key")
    print()
    
    # Step 3: Example queries
    print("=" * 80)
    print("💡 EXAMPLE QUERIES")
    print("=" * 80)
    print()
    
    examples = [
        {
            "category": "File Search (Internal Documents)",
            "queries": [
                "Search our docs for API authentication methods",
                "Find information about our security policies",
                "What coding standards do we follow?"
            ]
        },
        {
            "category": "Web Search (Current Information)",
            "queries": [
                "What are the latest AI developments this week?",
                "Current weather forecast",
                "Recent tech industry news"
            ]
        },
        {
            "category": "Hybrid (Both Sources)",
            "queries": [
                "Compare our API docs with modern REST best practices",
                "How do our security policies align with current standards?",
                "What's the difference between our ML approach and latest research?"
            ]
        }
    ]
    
    for example in examples:
        print(f"📌 {example['category']}")
        print()
        for i, query in enumerate(example['queries'], 1):
            print(f"   {i}. {query}")
        print()
    
    # Step 4: Interactive mode prompt
    print("=" * 80)
    print("🚀 TRY IT YOURSELF")
    print("=" * 80)
    print()
    print("To run queries interactively:")
    print()
    print("1. Make sure Qdrant is running:")
    print("   docker run -p 6333:6333 qdrant/qdrant")
    print()
    print("2. Create a 'vector_store' collection with your documents")
    print()
    print("3. (Optional) Get Brave Search API key:")
    print("   https://brave.com/search/api/")
    print()
    print("4. Run queries:")
    print()
    print("   response = triage_agent.chat('Your query here')")
    print("   print(response['content'])")
    print()
    
    # Step 5: Quick test (if user wants)
    print("=" * 80)
    print("🧪 QUICK TEST")
    print("=" * 80)
    print()
    
    print("Want to test with a sample query? (requires Qdrant running)")
    user_input = input("Enter 'y' to test or any other key to skip: ").strip().lower()
    
    if user_input == 'y':
        print()
        print("Testing: List available collections in Qdrant...")
        print("-" * 80)
        
        try:
            # Test the file search agent directly
            response = file_agent.chat("List all available collections")
            print("\n🤖 Response:")
            print(response.get('content', 'No response'))
            print()
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print()
            print("Tips:")
            print("  - Make sure Qdrant is running: docker run -p 6333:6333 qdrant/qdrant")
            print("  - Check that the Qdrant service is accessible at localhost:6333")
            print()
    else:
        print("\nSkipping test. Run this demo again when Qdrant is ready!")
        print()
    
    # Step 6: Next steps
    print("=" * 80)
    print("📚 NEXT STEPS")
    print("=" * 80)
    print()
    print("1. Read the full documentation:")
    print("   examples/COLLABORATIVE_AGENTS_README.md")
    print()
    print("2. Explore the source code:")
    print("   examples/collaborative_agents_example.py")
    print()
    print("3. Customize for your use case:")
    print("   - Add more specialized agents")
    print("   - Create custom tools")
    print("   - Integrate with your systems")
    print()
    print("4. Check out other examples:")
    print("   - basic_examples.py")
    print("   - web_search_examples.py")
    print("   - advanced_examples.py")
    print()
    
    print("=" * 80)
    print("✨ Happy coding with collaborative agents!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")
        import traceback
        traceback.print_exc()
