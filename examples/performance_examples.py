"""
Examples of using performance optimization features.
"""

from ollama_agents import Agent, tool
from ollama_agents.performance import (
    enable_response_caching, get_response_cache,
    LRUCache, RequestBatcher
)

# Example 1: Response caching
print("=" * 80)
print("Example 1: Response Caching")
print("=" * 80)

# Enable caching
enable_response_caching(max_size=100, ttl_seconds=3600)
print("✅ Response caching enabled\n")

agent = Agent(
    name="assistant",
    model="qwen2.5-coder:3b-instruct-q8_0",
    instructions="You are a helpful assistant."
)

# First call - will be cached
print("First call (no cache):")
response1 = agent.chat("What is Python?")
print(f"Response: {response1['content'][:100]}...\n")

# Second call - should hit cache
print("Second call (from cache):")
response2 = agent.chat("What is Python?")
print(f"Response: {response2['content'][:100]}...\n")

# Check cache stats
cache = get_response_cache()
if cache:
    stats = cache.get_stats()
    print(f"Cache stats: {stats}\n")

# Example 2: LRU Cache
print("=" * 80)
print("Example 2: LRU Cache for Custom Data")
print("=" * 80)

cache = LRUCache(max_size=10, max_memory_mb=1)

# Store some data
for i in range(15):
    cache.set(f"key_{i}", f"value_{i}" * 100)
    print(f"Stored key_{i}")

print(f"\nCache size: {cache.get_stats()['size']} (max: 10)")
print(f"Cache stats: {cache.get_stats()}")

# Retrieve data
print("\nRetrieving data:")
for i in range(5, 10):
    value = cache.get(f"key_{i}")
    print(f"key_{i}: {'Found' if value else 'Not found (evicted)'}")

print(f"\nFinal cache stats: {cache.get_stats()}\n")

# Example 3: Request Batching
print("=" * 80)
print("Example 3: Request Batching")
print("=" * 80)

batcher = RequestBatcher(batch_size=5, max_wait_ms=100)

# Define a batch processor
def process_batch(items):
    """Process a batch of items"""
    print(f"Processing batch of {len(items)} items")
    return [f"Processed: {item}" for item in items]

batcher.set_processor(process_batch)

# Simulate adding requests
import threading

def add_request(req_id, data):
    result = batcher.add_request(req_id, data)
    print(f"Request {req_id}: {result}")

threads = []
for i in range(12):
    t = threading.Thread(target=add_request, args=(f"req_{i}", f"data_{i}"))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("\n✅ Batching example complete\n")

# Example 4: Memory-efficient caching
print("=" * 80)
print("Example 4: Memory-Efficient Caching")
print("=" * 80)

# Create cache with small memory limit
cache = LRUCache(max_size=1000, max_memory_mb=0.1)  # Only 100KB

# Try to store large items
large_data = "x" * 50000  # 50KB
cache.set("large_1", large_data)
print(f"Stored large_1: {cache.get_stats()['memory_mb']:.4f} MB")

cache.set("large_2", large_data)
print(f"Stored large_2: {cache.get_stats()['memory_mb']:.4f} MB")

cache.set("large_3", large_data)
print(f"Stored large_3: {cache.get_stats()['memory_mb']:.4f} MB")

print(f"\nEvictions: {cache.get_stats()['evictions']}")
print(f"Final size: {cache.get_stats()['size']}")
print(f"Memory used: {cache.get_stats()['memory_mb']:.4f} MB")

# Check what's still in cache
print("\nChecking cache contents:")
for i in range(1, 4):
    value = cache.get(f"large_{i}")
    print(f"large_{i}: {'Found' if value else 'Evicted'}")

print("\n" + "=" * 80)
print("✅ Performance optimization examples complete!")
print("=" * 80)
