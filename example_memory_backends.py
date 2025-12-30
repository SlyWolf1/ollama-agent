#!/usr/bin/env python3
"""
Examples of different memory storage backends for ollama_agents
"""
from ollama_agents import Agent, SQLiteMemoryStore, InMemoryStore


def example_sqlite_backend():
    """Example using SQLite backend"""
    print("=== SQLite Memory Backend Example ===")
    
    # Use file-based SQLite storage
    sqlite_store = SQLiteMemoryStore("agent_data.db")
    agent = Agent(
        name="sqlite_agent",
        instructions="You are an agent using SQLite for memory.",
        enable_memory=True,
        memory_store=sqlite_store
    )
    
    agent.remember("project_name", "AI Assistant Development")
    agent.remember("deadline", "2023-12-31", metadata={"priority": "high"})
    
    print(f"Project: {agent.recall('project_name')}")
    print(f"Deadline: {agent.recall('deadline')}")
    print(f"Metadata: {agent.get_memory_metadata('deadline')}")
    
    print("SQLite example completed.\n")


def example_in_memory_backend():
    """Example using in-memory backend (for temporary storage)"""
    print("=== In-Memory Backend Example ===")
    
    # Use in-memory storage (data is lost when program ends)
    memory_store = InMemoryStore()
    agent = Agent(
        name="memory_agent",
        instructions="You are an agent using in-memory storage.",
        enable_memory=True,
        memory_store=memory_store
    )
    
    agent.remember("session_id", "sess_12345")
    agent.remember("current_task", "Processing user request")
    
    print(f"Session ID: {agent.recall('session_id')}")
    print(f"Current task: {agent.recall('current_task')}")
    
    print("In-memory example completed.\n")


def example_default_memory():
    """Example using default memory (which uses in-memory store)"""
    print("=== Default Memory Example ===")
    
    # Agent with memory enabled but no specific store (uses default)
    agent = Agent(
        name="default_agent",
        instructions="You are an agent using default memory.",
        enable_memory=True  # This will use the default in-memory store
    )
    
    agent.remember("user_id", "user_67890")
    agent.remember("preferences", {"theme": "dark", "language": "en"})
    
    print(f"User ID: {agent.recall('user_id')}")
    print(f"Preferences: {agent.recall('preferences')}")
    
    print("Default memory example completed.\n")


if __name__ == "__main__":
    print("Ollama Agents Memory Backend Examples\n")
    
    example_sqlite_backend()
    example_in_memory_backend()
    example_default_memory()
    
    print("All memory backend examples completed!")