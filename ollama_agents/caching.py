"""
Caching functionality for Ollama Agents SDK
Provides response caching to improve performance and reduce API calls
"""
import hashlib
import json
import time
from typing import Any, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class CacheStrategy(Enum):
    """Cache eviction strategies"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    timestamp: float
    access_count: int = 0
    last_access: float = 0.0
    ttl: Optional[float] = None

    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        if self.ttl is None:
            return False
        return (time.time() - self.timestamp) > self.ttl

    def access(self):
        """Record an access to this cache entry"""
        self.access_count += 1
        self.last_access = time.time()


class ResponseCache:
    """
    Cache for agent responses with configurable strategies
    """

    def __init__(
        self,
        max_size: int = 1000,
        strategy: CacheStrategy = CacheStrategy.LRU,
        default_ttl: Optional[float] = None
    ):
        """
        Initialize response cache
        
        Args:
            max_size: Maximum number of entries in cache
            strategy: Cache eviction strategy
            default_ttl: Default time-to-live in seconds (None = no expiration)
        """
        self.max_size = max_size
        self.strategy = strategy
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.hits = 0
        self.misses = 0

    def _generate_key(
        self,
        message: str,
        model: str,
        options: Optional[Dict[str, Any]] = None,
        tools: Optional[list] = None
    ) -> str:
        """
        Generate a cache key from request parameters
        
        Args:
            message: User message
            model: Model name
            options: Model options
            tools: Tools list
            
        Returns:
            str: Cache key (SHA256 hash)
        """
        # Create a deterministic representation
        cache_data = {
            "message": message,
            "model": model,
            "options": options or {},
            "tools": [str(t) for t in (tools or [])]
        }
        
        # Sort keys for consistency
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_str.encode()).hexdigest()

    def get(
        self,
        message: str,
        model: str,
        options: Optional[Dict[str, Any]] = None,
        tools: Optional[list] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached response if available
        
        Returns:
            Cached response or None if not found/expired
        """
        key = self._generate_key(message, model, options, tools)
        
        if key not in self.cache:
            self.misses += 1
            return None
        
        entry = self.cache[key]
        
        # Check expiration
        if entry.is_expired():
            del self.cache[key]
            self.misses += 1
            return None
        
        # Record access
        entry.access()
        self.hits += 1
        
        return entry.value

    def set(
        self,
        message: str,
        model: str,
        response: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None,
        tools: Optional[list] = None,
        ttl: Optional[float] = None
    ):
        """
        Cache a response
        
        Args:
            message: User message
            model: Model name
            response: Response to cache
            options: Model options
            tools: Tools list
            ttl: Time-to-live in seconds (overrides default)
        """
        # Evict if necessary
        if len(self.cache) >= self.max_size:
            self._evict()
        
        key = self._generate_key(message, model, options, tools)
        
        entry = CacheEntry(
            key=key,
            value=response,
            timestamp=time.time(),
            ttl=ttl if ttl is not None else self.default_ttl
        )
        entry.access()
        
        self.cache[key] = entry

    def _evict(self):
        """Evict entries based on strategy"""
        if not self.cache:
            return
        
        if self.strategy == CacheStrategy.LRU:
            # Remove least recently used
            oldest_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k].last_access
            )
            del self.cache[oldest_key]
        
        elif self.strategy == CacheStrategy.LFU:
            # Remove least frequently used
            least_used_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k].access_count
            )
            del self.cache[least_used_key]
        
        elif self.strategy == CacheStrategy.TTL:
            # Remove oldest entry
            oldest_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k].timestamp
            )
            del self.cache[oldest_key]

    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 2),
            "strategy": self.strategy.value
        }

    def invalidate(
        self,
        message: str,
        model: str,
        options: Optional[Dict[str, Any]] = None,
        tools: Optional[list] = None
    ):
        """Invalidate a specific cache entry"""
        key = self._generate_key(message, model, options, tools)
        if key in self.cache:
            del self.cache[key]


# Global cache instance
_global_cache: Optional[ResponseCache] = None


def get_cache() -> Optional[ResponseCache]:
    """Get the global cache instance"""
    return _global_cache


def enable_caching(
    max_size: int = 1000,
    strategy: CacheStrategy = CacheStrategy.LRU,
    default_ttl: Optional[float] = None
) -> ResponseCache:
    """
    Enable global caching
    
    Args:
        max_size: Maximum cache size
        strategy: Cache eviction strategy
        default_ttl: Default TTL in seconds
        
    Returns:
        ResponseCache instance
    """
    global _global_cache
    _global_cache = ResponseCache(max_size, strategy, default_ttl)
    return _global_cache


def disable_caching():
    """Disable global caching"""
    global _global_cache
    _global_cache = None
