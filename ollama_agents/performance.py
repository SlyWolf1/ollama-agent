"""
Performance optimizations for Ollama agents.
Includes caching, batching, and connection pooling.
"""

import time
import hashlib
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import OrderedDict
import threading
from .logger import get_logger

logger = get_logger()


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    timestamp: datetime
    hits: int = 0
    size_bytes: int = 0


class LRUCache:
    """Least Recently Used cache with size limits"""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.total_size_bytes = 0
        self._lock = threading.Lock()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                entry.hits += 1
                self.cache.move_to_end(key)
                self.stats["hits"] += 1
                logger.debug(f"💾 Cache HIT: {key[:50]}")
                return entry.value
            
            self.stats["misses"] += 1
            logger.debug(f"❌ Cache MISS: {key[:50]}")
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache"""
        with self._lock:
            # Calculate size
            size_bytes = len(str(value))
            
            # Remove old entry if exists
            if key in self.cache:
                old_entry = self.cache[key]
                self.total_size_bytes -= old_entry.size_bytes
                del self.cache[key]
            
            # Evict if necessary
            while (len(self.cache) >= self.max_size or 
                   self.total_size_bytes + size_bytes > self.max_memory_bytes):
                if not self.cache:
                    break
                self._evict_oldest()
            
            # Add new entry
            entry = CacheEntry(
                key=key,
                value=value,
                timestamp=datetime.now(),
                size_bytes=size_bytes
            )
            self.cache[key] = entry
            self.total_size_bytes += size_bytes
            
            logger.debug(f"💾 Cache SET: {key[:50]} ({size_bytes} bytes)")
    
    def _evict_oldest(self):
        """Evict oldest entry"""
        if self.cache:
            key, entry = self.cache.popitem(last=False)
            self.total_size_bytes -= entry.size_bytes
            self.stats["evictions"] += 1
            logger.debug(f"🗑️ Cache EVICT: {key[:50]}")
    
    def clear(self):
        """Clear entire cache"""
        with self._lock:
            self.cache.clear()
            self.total_size_bytes = 0
            logger.info("🧹 Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            hit_rate = 0
            if self.stats["hits"] + self.stats["misses"] > 0:
                hit_rate = self.stats["hits"] / (self.stats["hits"] + self.stats["misses"])
            
            return {
                **self.stats,
                "hit_rate": hit_rate,
                "size": len(self.cache),
                "memory_mb": self.total_size_bytes / (1024 * 1024)
            }


class RequestBatcher:
    """Batch multiple requests for efficiency"""
    
    def __init__(self, batch_size: int = 10, max_wait_ms: int = 100):
        self.batch_size = batch_size
        self.max_wait_ms = max_wait_ms
        self.pending: List[Dict[str, Any]] = []
        self.results: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
        self._processor: Optional[Callable] = None
    
    def add_request(self, request_id: str, data: Any) -> Any:
        """Add request to batch"""
        with self._condition:
            self.pending.append({"id": request_id, "data": data})
            
            # Process if batch is full
            if len(self.pending) >= self.batch_size:
                self._process_batch()
            else:
                # Wait for batch to fill or timeout
                self._condition.wait(timeout=self.max_wait_ms / 1000.0)
                if self.pending and request_id in [r["id"] for r in self.pending]:
                    self._process_batch()
            
            # Return result
            return self.results.pop(request_id, None)
    
    def set_processor(self, processor: Callable[[List[Any]], List[Any]]):
        """Set batch processor function"""
        self._processor = processor
    
    def _process_batch(self):
        """Process current batch"""
        if not self.pending or not self._processor:
            return
        
        logger.debug(f"⚡ Processing batch of {len(self.pending)} requests")
        
        # Extract data
        batch_data = [r["data"] for r in self.pending]
        batch_ids = [r["id"] for r in self.pending]
        
        # Process
        try:
            results = self._processor(batch_data)
            
            # Store results
            for req_id, result in zip(batch_ids, results):
                self.results[req_id] = result
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
        
        # Clear pending
        self.pending.clear()
        self._condition.notify_all()


class ConnectionPool:
    """Connection pool for managing resources"""
    
    def __init__(self, factory: Callable, max_connections: int = 10):
        self.factory = factory
        self.max_connections = max_connections
        self.available: List[Any] = []
        self.in_use: set = set()
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
    
    def acquire(self, timeout: Optional[float] = None) -> Any:
        """Acquire a connection from pool"""
        with self._condition:
            start_time = time.time()
            
            while True:
                # Try to get available connection
                if self.available:
                    conn = self.available.pop()
                    self.in_use.add(id(conn))
                    logger.debug(f"🔌 Connection acquired (pool: {len(self.available)})")
                    return conn
                
                # Create new if under limit
                if len(self.in_use) < self.max_connections:
                    conn = self.factory()
                    self.in_use.add(id(conn))
                    logger.debug(f"🔌 New connection created (pool: {len(self.available)})")
                    return conn
                
                # Wait for available connection
                if timeout:
                    elapsed = time.time() - start_time
                    remaining = timeout - elapsed
                    if remaining <= 0:
                        raise TimeoutError("Connection pool timeout")
                    self._condition.wait(remaining)
                else:
                    self._condition.wait()
    
    def release(self, conn: Any):
        """Release connection back to pool"""
        with self._condition:
            conn_id = id(conn)
            if conn_id in self.in_use:
                self.in_use.remove(conn_id)
                self.available.append(conn)
                self._condition.notify()
                logger.debug(f"🔌 Connection released (pool: {len(self.available)})")
    
    def close_all(self):
        """Close all connections"""
        with self._lock:
            for conn in self.available:
                if hasattr(conn, 'close'):
                    conn.close()
            self.available.clear()
            self.in_use.clear()
            logger.info("🔌 All connections closed")


class ResponseCache:
    """Cache for LLM responses based on prompt hashing"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.cache = LRUCache(max_size=max_size)
        self.ttl = timedelta(seconds=ttl_seconds)
    
    def get_cache_key(self, model: str, messages: List[Dict], **params) -> str:
        """Generate cache key from request parameters"""
        cache_data = {
            "model": model,
            "messages": messages,
            "params": params
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_str.encode()).hexdigest()
    
    def get(self, model: str, messages: List[Dict], **params) -> Optional[Dict]:
        """Get cached response"""
        key = self.get_cache_key(model, messages, **params)
        entry = self.cache.get(key)
        
        if entry:
            # Check TTL
            if datetime.now() - entry.get("timestamp", datetime.now()) < self.ttl:
                return entry.get("response")
        
        return None
    
    def set(self, model: str, messages: List[Dict], response: Dict, **params):
        """Cache response"""
        key = self.get_cache_key(model, messages, **params)
        entry = {
            "response": response,
            "timestamp": datetime.now()
        }
        self.cache.set(key, entry)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache.get_stats()


# Global instances
_response_cache: Optional[ResponseCache] = None
_connection_pool: Optional[ConnectionPool] = None


def enable_response_caching(max_size: int = 1000, ttl_seconds: int = 3600):
    """Enable response caching"""
    global _response_cache
    _response_cache = ResponseCache(max_size=max_size, ttl_seconds=ttl_seconds)
    logger.info(f"✅ Response caching enabled (max_size={max_size}, ttl={ttl_seconds}s)")


def get_response_cache() -> Optional[ResponseCache]:
    """Get global response cache"""
    return _response_cache


def enable_connection_pooling(factory: Callable, max_connections: int = 10):
    """Enable connection pooling"""
    global _connection_pool
    _connection_pool = ConnectionPool(factory=factory, max_connections=max_connections)
    logger.info(f"✅ Connection pooling enabled (max={max_connections})")


def get_connection_pool() -> Optional[ConnectionPool]:
    """Get global connection pool"""
    return _connection_pool
