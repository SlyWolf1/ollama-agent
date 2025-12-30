#!/usr/bin/env python3
"""
Example demonstrating the memory functionality in ollama_agents
"""
from ollama_agents import Agent, SQLiteMemoryStore


def example_memory_usage():
    """Example showing how to use the memory functionality"""
    print("=== Ollama Agents Memory Example ===\n")
    
    # Create an agent with memory enabled using SQLite storage
    agent = Agent(
        name="assistant",
        instructions="You are a helpful assistant that remembers user information.",
        enable_memory=True,
        memory_store=SQLiteMemoryStore("example_memory.db")  # Using file-based SQLite
    )
    
    # Simulate a conversation where the agent remembers user information
    print("1. User introduces themselves:")
    user_name = "Alice Johnson"
    user_preferences = {
        "favorite_color": "purple",
        "dietary_restrictions": ["vegetarian"],
        "hobbies": ["reading", "hiking", "photography"]
    }
    
    # Store user information in memory
    agent.remember("user_name", user_name)
    agent.remember("preferences", user_preferences)
    agent.remember("conversation_start_time", "2023-06-15 10:00:00", metadata={"type": "session_info"})
    
    print(f"   - Stored user name: {user_name}")
    print(f"   - Stored preferences: {user_preferences}")
    
    # Later in the conversation, retrieve the information
    print("\n2. Later in conversation, agent recalls user info:")
    recalled_name = agent.recall("user_name")
    recalled_preferences = agent.recall("preferences")
    
    print(f"   - Recalled user name: {recalled_name}")
    print(f"   - Recalled preferences: {recalled_preferences}")
    
    # Show all memory keys
    print(f"\n3. All memory keys for agent: {agent.get_memory_keys()}")
    
    # Example of temporary memory with expiration
    print("\n4. Storing temporary information with expiration:")
    agent.remember("temporary_note", "Remember to follow up on project", expires_in=10)  # Expires in 10 seconds
    temp_note = agent.recall("temporary_note")
    print(f"   - Temporary note: {temp_note}")
    
    # Example of using metadata
    print("\n5. Using metadata for memory entries:")
    agent.remember("user_email", "alice@example.com", metadata={"sensitivity": "high", "category": "contact_info"})
    email_metadata = agent.get_memory_metadata("user_email")
    print(f"   - Email metadata: {email_metadata}")
    
    # Example of forgetting specific information
    print("\n6. Forgetting specific information:")
    agent.remember("temporary_task", "Send meeting notes")
    print(f"   - Before forgetting: {agent.get_memory_keys()}")
    agent.forget("temporary_task")
    print(f"   - After forgetting 'temporary_task': {agent.get_memory_keys()}")
    
    print("\n=== Memory Example Completed ===")


def example_multiple_agents():
    """Example showing memory isolation between different agents"""
    print("\n=== Multiple Agents Memory Isolation Example ===\n")
    
    # Create two different agents
    agent1 = Agent(
        name="sales_agent",
        instructions="You are a sales assistant.",
        enable_memory=True
    )
    
    agent2 = Agent(
        name="support_agent", 
        instructions="You are a support assistant.",
        enable_memory=True
    )
    
    # Each agent stores different information
    agent1.remember("customer_name", "John Smith")
    agent1.remember("purchase_history", ["laptop", "mouse", "keyboard"])
    
    agent2.remember("ticket_id", "TKT-12345")
    agent2.remember("issue_description", "Product not working properly")
    
    print(f"Sales agent memory keys: {agent1.get_memory_keys()}")
    print(f"Support agent memory keys: {agent2.get_memory_keys()}")
    
    # Verify isolation - each agent only sees its own memory
    print(f"Sales agent recalls customer_name: {agent1.recall('customer_name')}")
    print(f"Support agent recalls customer_name: {agent2.recall('customer_name')}")  # Should be None
    
    print(f"Support agent recalls ticket_id: {agent2.recall('ticket_id')}")
    print(f"Sales agent recalls ticket_id: {agent1.recall('ticket_id')}")  # Should be None
    
    print("\n=== Multiple Agents Example Completed ===")


if __name__ == "__main__":
    example_memory_usage()
    example_multiple_agents()