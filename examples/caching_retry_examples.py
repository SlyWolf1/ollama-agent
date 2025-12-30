"""
Examples demonstrating caching and retry features
"""
import time
from ollama_agents import (
    Agent, 
    ResponseCache, 
    CacheStrategy,
    RetryConfig,
    enable_caching
)


def caching_example():
    """Demonstrate response caching"""
    print("=== Caching Example ===\n")
    
    # Enable global caching
    cache = enable_caching(max_size=100, strategy=CacheStrategy.LRU, default_ttl=3600)
    
    # Create agent with caching enabled
    agent = Agent(
        name="cached_agent",
        model="qwen3-vl:2b-thinking-q8_0",
        instructions="You are a helpful assistant.",
        enable_cache=True
    )
    
    question = "What is 2 + 2?"
    
    # First call - will hit the API
    print("First call (cache miss):")
    start = time.time()
    response1 = agent.chat(question)
    time1 = time.time() - start
    print(f"Response: {response1['content'][:100]}")
    print(f"Time: {time1:.2f}s")
    print(f"Cache stats: {cache.get_stats()}\n")
    
    # Second call - should be cached
    print("Second call (cache hit):")
    start = time.time()
    response2 = agent.chat(question)
    time2 = time.time() - start
    print(f"Response: {response2['content'][:100]}")
    print(f"Time: {time2:.2f}s")
    print(f"Cache stats: {cache.get_stats()}\n")
    
    print(f"Speed improvement: {time1/time2:.1f}x faster!")
    print()


def retry_example():
    """Demonstrate retry functionality"""
    print("=== Retry Example ===\n")
    
    # Create agent with retry enabled
    retry_config = RetryConfig(
        max_retries=3,
        initial_delay=1.0,
        exponential_base=2.0,
        jitter=True
    )
    
    agent = Agent(
        name="retry_agent",
        model="qwen3-vl:2b-thinking-q8_0",
        instructions="You are a helpful assistant.",
        enable_retry=True,
        retry_config=retry_config
    )
    
    print("Agent configured with retry:")
    print(f"- Max retries: {retry_config.max_retries}")
    print(f"- Initial delay: {retry_config.initial_delay}s")
    print(f"- Exponential base: {retry_config.exponential_base}")
    print()
    
    # This will automatically retry on connection errors
    try:
        response = agent.chat("Explain quantum computing in simple terms.")
        print(f"Response: {response['content'][:150]}...")
    except Exception as e:
        print(f"Error after retries: {e}")
    
    print()


def cache_with_ttl_example():
    """Demonstrate cache with TTL (time-to-live)"""
    print("=== Cache with TTL Example ===\n")
    
    # Create cache with 5-second TTL
    cache = ResponseCache(
        max_size=100,
        strategy=CacheStrategy.TTL,
        default_ttl=5.0  # 5 seconds
    )
    
    agent = Agent(
        name="ttl_agent",
        model="qwen3-vl:2b-thinking-q8_0",
        instructions="You are a helpful assistant.",
        enable_cache=True,
        cache=cache
    )
    
    question = "What is the capital of France?"
    
    print("First call:")
    response1 = agent.chat(question)
    print(f"Response: {response1['content'][:100]}")
    print(f"Cache stats: {cache.get_stats()}\n")
    
    print("Immediate second call (cached):")
    response2 = agent.chat(question)
    print(f"Response: {response2['content'][:100]}")
    print(f"Cache stats: {cache.get_stats()}\n")
    
    print("Waiting 6 seconds for cache to expire...")
    time.sleep(6)
    
    print("Third call after expiration (cache miss):")
    response3 = agent.chat(question)
    print(f"Response: {response3['content'][:100]}")
    print(f"Cache stats: {cache.get_stats()}\n")


def combined_example():
    """Demonstrate caching and retry together"""
    print("=== Combined Caching + Retry Example ===\n")
    
    # Enable caching
    cache = enable_caching(max_size=50, strategy=CacheStrategy.LRU)
    
    # Create agent with both features
    agent = Agent(
        name="combined_agent",
        model="qwen3-vl:2b-thinking-q8_0",
        instructions="You are a helpful assistant.",
        enable_cache=True,
        enable_retry=True,
        retry_config=RetryConfig(max_retries=3, initial_delay=0.5)
    )
    
    questions = [
        "What is machine learning?",
        "What is deep learning?",
        "What is machine learning?",  # Duplicate - should be cached
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"Question {i}: {question}")
        start = time.time()
        try:
            response = agent.chat(question)
            elapsed = time.time() - start
            print(f"Response: {response['content'][:80]}...")
            print(f"Time: {elapsed:.2f}s")
        except Exception as e:
            print(f"Error: {e}")
        print()
    
    print(f"Final cache stats: {cache.get_stats()}")
    print()


if __name__ == "__main__":
    # Run examples
    print("=" * 60)
    print("Caching and Retry Examples")
    print("=" * 60)
    print()
    
    caching_example()
    retry_example()
    cache_with_ttl_example()
    combined_example()
    
    print("All examples completed!")
