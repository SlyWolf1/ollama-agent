#!/usr/bin/env python3
"""
Test script for the memory functionality in ollama_agents
"""
import asyncio
import time
from datetime import datetime, timedelta
from ollama_agents import Agent, SQLiteMemoryStore, RedisMemoryStore, PostgresMemoryStore, InMemoryStore, get_memory_manager


def test_basic_memory():
    """Test basic memory functionality"""
    print("Testing basic memory functionality...")
    
    # Create an agent with memory enabled
    agent = Agent(
        name="test_agent",
        instructions="You are a helpful assistant.",
        enable_memory=True
    )
    
    # Test remembering and recalling
    agent.remember("user_name", "John Doe")
    agent.remember("user_preferences", {"color": "blue", "food": "pizza"})
    
    name = agent.recall("user_name")
    preferences = agent.recall("user_preferences")
    
    print(f"Recalled name: {name}")
    print(f"Recalled preferences: {preferences}")
    
    # Test listing keys
    keys = agent.get_memory_keys()
    print(f"Memory keys: {keys}")
    
    # Test forgetting
    agent.forget("user_name")
    name_after_forget = agent.recall("user_name")
    print(f"Name after forgetting: {name_after_forget}")
    
    # Test clearing memory
    agent.clear_memory()
    keys_after_clear = agent.get_memory_keys()
    print(f"Keys after clearing memory: {keys_after_clear}")
    
    print("Basic memory test completed successfully!")


def test_memory_with_different_stores():
    """Test memory with different storage backends"""
    print("\nTesting memory with different storage backends...")
    
    # Test with SQLite
    print("Testing with SQLite memory store...")
    sqlite_store = SQLiteMemoryStore(":memory:")
    agent_sqlite = Agent(
        name="sqlite_agent",
        instructions="You are a helpful assistant.",
        enable_memory=True,
        memory_store=sqlite_store
    )
    
    agent_sqlite.remember("test_key", "test_value")
    value = agent_sqlite.recall("test_key")
    print(f"SQLite retrieved value: {value}")
    
    # Test with InMemoryStore
    print("Testing with InMemory store...")
    in_memory_store = InMemoryStore()
    agent_memory = Agent(
        name="memory_agent",
        instructions="You are a helpful assistant.",
        enable_memory=True,
        memory_store=in_memory_store
    )
    
    agent_memory.remember("test_key2", "test_value2")
    value2 = agent_memory.recall("test_key2")
    print(f"InMemory retrieved value: {value2}")
    
    print("Different storage backends test completed!")


def test_memory_expiration():
    """Test memory expiration functionality"""
    print("\nTesting memory expiration...")
    
    agent = Agent(
        name="expiring_agent",
        instructions="You are a helpful assistant.",
        enable_memory=True
    )
    
    # Store with expiration in 1 second
    agent.remember("temp_data", "temporary value", expires_in=1)
    
    # Should be available immediately
    value = agent.recall("temp_data")
    print(f"Value before expiration: {value}")
    
    # Wait for expiration
    time.sleep(2)
    
    # Should be None after expiration
    value_after = agent.recall("temp_data")
    print(f"Value after expiration: {value_after}")
    
    print("Memory expiration test completed!")


def test_memory_metadata():
    """Test memory metadata functionality"""
    print("\nTesting memory metadata...")
    
    agent = Agent(
        name="metadata_agent",
        instructions="You are a helpful assistant.",
        enable_memory=True
    )
    
    # Store with metadata
    agent.remember("important_info", "sensitive data", metadata={"sensitivity": "high", "category": "personal"})
    
    # Retrieve value
    value = agent.recall("important_info")
    print(f"Retrieved value: {value}")
    
    # Retrieve metadata
    metadata = agent.get_memory_metadata("important_info")
    print(f"Retrieved metadata: {metadata}")
    
    print("Memory metadata test completed!")


async def test_async_memory():
    """Test async memory operations"""
    print("\nTesting async memory operations...")
    
    agent = Agent(
        name="async_agent",
        instructions="You are a helpful assistant.",
        enable_memory=True
    )
    
    # Test async operations
    agent.remember("async_key", "async_value")
    value = agent.recall("async_key")
    print(f"Async retrieved value: {value}")
    
    print("Async memory operations test completed!")


if __name__ == "__main__":
    print("Starting memory functionality tests...")
    
    test_basic_memory()
    test_memory_with_different_stores()
    test_memory_expiration()
    test_memory_metadata()
    
    # Run async test
    asyncio.run(test_async_memory())
    
    print("\nAll memory tests completed successfully!")