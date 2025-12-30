"""
Memory system for Ollama Agents with support for PostgreSQL, SQLite, Redis, and other storage backends
"""
from __future__ import annotations
import json
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import sqlite3
import threading
from contextlib import contextmanager

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


@dataclass
class MemoryEntry:
    """Represents a single memory entry"""
    id: str
    agent_id: str
    key: str
    value: Any
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'key': self.key,
            'value': self.value,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MemoryEntry:
        return cls(
            id=data['id'],
            agent_id=data['agent_id'],
            key=data['key'],
            value=data['value'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data.get('metadata', {}),
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
        )


class MemoryStore(ABC):
    """Abstract base class for memory storage backends"""

    @abstractmethod
    def store(self, entry: MemoryEntry) -> bool:
        """Store a memory entry"""
        pass

    @abstractmethod
    def retrieve(self, agent_id: str, key: str) -> Optional[MemoryEntry]:
        """Retrieve a memory entry by agent_id and key"""
        pass

    @abstractmethod
    def delete(self, agent_id: str, key: str) -> bool:
        """Delete a memory entry by agent_id and key"""
        pass

    @abstractmethod
    def list_keys(self, agent_id: str) -> List[str]:
        """List all keys for an agent"""
        pass

    @abstractmethod
    def clear_agent_memory(self, agent_id: str) -> bool:
        """Clear all memory for an agent"""
        pass

    @abstractmethod
    def cleanup_expired(self) -> int:
        """Clean up expired entries and return count of deleted entries"""
        pass


class SQLiteMemoryStore(MemoryStore):
    """SQLite-based memory storage"""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._lock = threading.Lock()
        # For :memory: databases, we need to use check_same_thread=False to allow multiple connections
        # to share the same in-memory database
        if db_path == ":memory:":
            # Create a shared in-memory database connection
            self._shared_conn = sqlite3.connect(db_path, check_same_thread=False)
            self._shared_conn.execute('''
                CREATE TABLE IF NOT EXISTS memory (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT,
                    expires_at TEXT,
                    UNIQUE(agent_id, key)
                )
            ''')
            self._shared_conn.execute('CREATE INDEX IF NOT EXISTS idx_agent_id ON memory(agent_id)')
            self._shared_conn.execute('CREATE INDEX IF NOT EXISTS idx_expires_at ON memory(expires_at)')
        else:
            # For file-based databases, initialize schema directly
            with sqlite3.connect(db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS memory (
                        id TEXT PRIMARY KEY,
                        agent_id TEXT NOT NULL,
                        key TEXT NOT NULL,
                        value TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        metadata TEXT,
                        expires_at TEXT,
                        UNIQUE(agent_id, key)
                    )
                ''')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_agent_id ON memory(agent_id)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_expires_at ON memory(expires_at)')

    @contextmanager
    def _get_connection(self):
        """Get a database connection with proper context management"""
        if self.db_path == ":memory:":
            # Use the shared connection for in-memory database
            try:
                yield self._shared_conn
                self._shared_conn.commit()
            except Exception:
                self._shared_conn.rollback()
                raise
        else:
            # Create a new connection for file-based database
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

    def store(self, entry: MemoryEntry) -> bool:
        """Store a memory entry in SQLite"""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO memory
                    (id, agent_id, key, value, timestamp, metadata, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry.id,
                    entry.agent_id,
                    entry.key,
                    json.dumps(entry.value),
                    entry.timestamp.isoformat(),
                    json.dumps(entry.metadata),
                    entry.expires_at.isoformat() if entry.expires_at else None
                ))
                return cursor.rowcount > 0

    def retrieve(self, agent_id: str, key: str) -> Optional[MemoryEntry]:
        """Retrieve a memory entry from SQLite"""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, agent_id, key, value, timestamp, metadata, expires_at
                    FROM memory
                    WHERE agent_id = ? AND key = ?
                ''', (agent_id, key))
                row = cursor.fetchone()
                if row:
                    return MemoryEntry(
                        id=row[0],
                        agent_id=row[1],
                        key=row[2],
                        value=json.loads(row[3]),
                        timestamp=datetime.fromisoformat(row[4]),
                        metadata=json.loads(row[5]),
                        expires_at=datetime.fromisoformat(row[6]) if row[6] else None
                    )
                return None

    def delete(self, agent_id: str, key: str) -> bool:
        """Delete a memory entry from SQLite"""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM memory WHERE agent_id = ? AND key = ?', (agent_id, key))
                return cursor.rowcount > 0

    def list_keys(self, agent_id: str) -> List[str]:
        """List all keys for an agent in SQLite"""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT key FROM memory WHERE agent_id = ?', (agent_id,))
                return [row[0] for row in cursor.fetchall()]

    def clear_agent_memory(self, agent_id: str) -> bool:
        """Clear all memory for an agent in SQLite"""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM memory WHERE agent_id = ?', (agent_id,))
                return cursor.rowcount > 0

    def cleanup_expired(self) -> int:
        """Clean up expired entries in SQLite"""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM memory 
                    WHERE expires_at IS NOT NULL AND expires_at < ?
                ''', (datetime.now().isoformat(),))
                return cursor.rowcount


class RedisMemoryStore(MemoryStore):
    """Redis-based memory storage"""

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, password: Optional[str] = None):
        if not REDIS_AVAILABLE:
            raise ImportError("redis package is required for RedisMemoryStore")
        
        self.redis_client = redis.Redis(host=host, port=port, db=db, password=password, decode_responses=False)
        self.prefix = "ollama:memory:"

    def _get_key(self, agent_id: str, key: str) -> str:
        """Generate a Redis key for the agent and key combination"""
        return f"{self.prefix}{agent_id}:{key}"

    def _get_agent_pattern(self, agent_id: str) -> str:
        """Generate a Redis pattern to match all keys for an agent"""
        return f"{self.prefix}{agent_id}:*"

    def store(self, entry: MemoryEntry) -> bool:
        """Store a memory entry in Redis"""
        redis_key = self._get_key(entry.agent_id, entry.key)
        data = entry.to_dict()
        serialized_data = json.dumps(data)
        
        if entry.expires_at:
            ttl = (entry.expires_at - datetime.now()).total_seconds()
            if ttl > 0:
                return self.redis_client.setex(redis_key, int(ttl), serialized_data)
            else:
                # Entry already expired, don't store it
                return False
        else:
            return self.redis_client.set(redis_key, serialized_data)

    def retrieve(self, agent_id: str, key: str) -> Optional[MemoryEntry]:
        """Retrieve a memory entry from Redis"""
        redis_key = self._get_key(agent_id, key)
        data = self.redis_client.get(redis_key)
        if data:
            try:
                entry_dict = json.loads(data.decode('utf-8'))
                return MemoryEntry.from_dict(entry_dict)
            except (json.JSONDecodeError, UnicodeDecodeError):
                return None
        return None

    def delete(self, agent_id: str, key: str) -> bool:
        """Delete a memory entry from Redis"""
        redis_key = self._get_key(agent_id, key)
        return bool(self.redis_client.delete(redis_key))

    def list_keys(self, agent_id: str) -> List[str]:
        """List all keys for an agent in Redis"""
        pattern = self._get_agent_pattern(agent_id)
        keys = self.redis_client.keys(pattern)
        # Remove prefix to get just the key part
        return [key.decode('utf-8').split(':')[-1] for key in keys]

    def clear_agent_memory(self, agent_id: str) -> bool:
        """Clear all memory for an agent in Redis"""
        pattern = self._get_agent_pattern(agent_id)
        keys = self.redis_client.keys(pattern)
        if keys:
            return bool(self.redis_client.delete(*keys))
        return True

    def cleanup_expired(self) -> int:
        """Redis automatically handles expiration, so this is a no-op"""
        # Redis handles expiration automatically, so we just return 0
        return 0


class PostgresMemoryStore(MemoryStore):
    """PostgreSQL-based memory storage"""

    def __init__(self, connection_string: str):
        if not POSTGRES_AVAILABLE:
            raise ImportError("psycopg2 package is required for PostgresMemoryStore")

        self.connection_string = connection_string
        self._lock = threading.Lock()
        # Initialize the database schema
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS memory (
                        id TEXT PRIMARY KEY,
                        agent_id TEXT NOT NULL,
                        key TEXT NOT NULL,
                        value JSONB NOT NULL,
                        timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                        metadata JSONB NOT NULL DEFAULT '{}',
                        expires_at TIMESTAMP WITH TIME ZONE,
                        UNIQUE(agent_id, key)
                    )
                ''')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_agent_id ON memory(agent_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_expires_at ON memory(expires_at)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_created_at ON memory(timestamp)')
            conn.commit()

    def _init_db(self):
        """Initialize the database schema"""
        # Create the table in the database
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS memory (
                        id TEXT PRIMARY KEY,
                        agent_id TEXT NOT NULL,
                        key TEXT NOT NULL,
                        value JSONB NOT NULL,
                        timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                        metadata JSONB NOT NULL DEFAULT '{}',
                        expires_at TIMESTAMP WITH TIME ZONE,
                        UNIQUE(agent_id, key)
                    )
                ''')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_agent_id ON memory(agent_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_expires_at ON memory(expires_at)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_created_at ON memory(timestamp)')
            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Get a database connection with proper context management"""
        conn = psycopg2.connect(self.connection_string)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def store(self, entry: MemoryEntry) -> bool:
        """Store a memory entry in PostgreSQL"""
        with self._lock:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute('''
                        INSERT INTO memory 
                        (id, agent_id, key, value, timestamp, metadata, expires_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (agent_id, key) 
                        DO UPDATE SET
                            value = EXCLUDED.value,
                            timestamp = EXCLUDED.timestamp,
                            metadata = EXCLUDED.metadata,
                            expires_at = EXCLUDED.expires_at
                    ''', (
                        entry.id,
                        entry.agent_id,
                        entry.key,
                        json.dumps(entry.value),
                        entry.timestamp,
                        json.dumps(entry.metadata),
                        entry.expires_at
                    ))
                    return True

    def retrieve(self, agent_id: str, key: str) -> Optional[MemoryEntry]:
        """Retrieve a memory entry from PostgreSQL"""
        with self._lock:
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute('''
                        SELECT id, agent_id, key, value, timestamp, metadata, expires_at
                        FROM memory
                        WHERE agent_id = %s AND key = %s
                    ''', (agent_id, key))
                    row = cursor.fetchone()
                    if row:
                        return MemoryEntry(
                            id=row['id'],
                            agent_id=row['agent_id'],
                            key=row['key'],
                            value=json.loads(row['value']),
                            timestamp=row['timestamp'],
                            metadata=json.loads(row['metadata']),
                            expires_at=row['expires_at']
                        )
                    return None

    def delete(self, agent_id: str, key: str) -> bool:
        """Delete a memory entry from PostgreSQL"""
        with self._lock:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute('DELETE FROM memory WHERE agent_id = %s AND key = %s', (agent_id, key))
                    return cursor.rowcount > 0

    def list_keys(self, agent_id: str) -> List[str]:
        """List all keys for an agent in PostgreSQL"""
        with self._lock:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute('SELECT key FROM memory WHERE agent_id = %s', (agent_id,))
                    return [row[0] for row in cursor.fetchall()]

    def clear_agent_memory(self, agent_id: str) -> bool:
        """Clear all memory for an agent in PostgreSQL"""
        with self._lock:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute('DELETE FROM memory WHERE agent_id = %s', (agent_id,))
                    return cursor.rowcount > 0

    def cleanup_expired(self) -> int:
        """Clean up expired entries in PostgreSQL"""
        with self._lock:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute('''
                        DELETE FROM memory 
                        WHERE expires_at IS NOT NULL AND expires_at < NOW()
                    ''')
                    return cursor.rowcount


class InMemoryStore(MemoryStore):
    """Simple in-memory storage for development/testing"""
    
    def __init__(self):
        self._store: Dict[str, MemoryEntry] = {}
        self._lock = threading.Lock()

    def store(self, entry: MemoryEntry) -> bool:
        """Store a memory entry in memory"""
        with self._lock:
            key = f"{entry.agent_id}:{entry.key}"
            self._store[key] = entry
            return True

    def retrieve(self, agent_id: str, key: str) -> Optional[MemoryEntry]:
        """Retrieve a memory entry from memory"""
        with self._lock:
            store_key = f"{agent_id}:{key}"
            return self._store.get(store_key)

    def delete(self, agent_id: str, key: str) -> bool:
        """Delete a memory entry from memory"""
        with self._lock:
            store_key = f"{agent_id}:{key}"
            if store_key in self._store:
                del self._store[store_key]
                return True
            return False

    def list_keys(self, agent_id: str) -> List[str]:
        """List all keys for an agent in memory"""
        with self._lock:
            keys = []
            for store_key in self._store.keys():
                if store_key.startswith(f"{agent_id}:"):
                    keys.append(store_key.split(":", 1)[1])
            return keys

    def clear_agent_memory(self, agent_id: str) -> bool:
        """Clear all memory for an agent in memory"""
        with self._lock:
            keys_to_delete = [key for key in self._store.keys() if key.startswith(f"{agent_id}:")]
            for key in keys_to_delete:
                del self._store[key]
            return True

    def cleanup_expired(self) -> int:
        """Clean up expired entries in memory"""
        with self._lock:
            now = datetime.now()
            expired_keys = [
                key for key, entry in self._store.items()
                if entry.expires_at and entry.expires_at < now
            ]
            for key in expired_keys:
                del self._store[key]
            return len(expired_keys)


class MemoryManager:
    """Manages memory operations for agents"""
    
    def __init__(self, store: MemoryStore):
        self.store = store

    def set(self, agent_id: str, key: str, value: Any, expires_in: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Set a memory value for an agent"""
        import uuid
        expires_at = None
        if expires_in:
            expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        entry = MemoryEntry(
            id=str(uuid.uuid4()),
            agent_id=agent_id,
            key=key,
            value=value,
            metadata=metadata or {},
            expires_at=expires_at
        )
        return self.store.store(entry)

    def get(self, agent_id: str, key: str) -> Optional[Any]:
        """Get a memory value for an agent"""
        entry = self.store.retrieve(agent_id, key)
        if entry:
            # Check if entry is expired
            if entry.expires_at and entry.expires_at < datetime.now():
                self.store.delete(agent_id, key)
                return None
            return entry.value
        return None

    def delete(self, agent_id: str, key: str) -> bool:
        """Delete a memory value for an agent"""
        return self.store.delete(agent_id, key)

    def list_keys(self, agent_id: str) -> List[str]:
        """List all memory keys for an agent"""
        return self.store.list_keys(agent_id)

    def clear_agent_memory(self, agent_id: str) -> bool:
        """Clear all memory for an agent"""
        return self.store.clear_agent_memory(agent_id)

    def cleanup_expired(self) -> int:
        """Clean up expired memory entries"""
        return self.store.cleanup_expired()

    def get_metadata(self, agent_id: str, key: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a memory entry"""
        entry = self.store.retrieve(agent_id, key)
        if entry:
            # Check if entry is expired
            if entry.expires_at and entry.expires_at < datetime.now():
                self.store.delete(agent_id, key)
                return None
            return entry.metadata
        return None


# Default memory manager instance
_default_memory_manager = None


def get_memory_manager(store: Optional[MemoryStore] = None) -> MemoryManager:
    """Get the global memory manager instance"""
    global _default_memory_manager
    if _default_memory_manager is None:
        if store is None:
            store = InMemoryStore()  # Default to in-memory store
        _default_memory_manager = MemoryManager(store)
    return _default_memory_manager


def set_memory_manager(manager: MemoryManager):
    """Set the global memory manager instance"""
    global _default_memory_manager
    _default_memory_manager = manager

# MongoDB Memory Store
try:
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False


if MONGODB_AVAILABLE:
    class MongoDBMemoryStore(MemoryStore):
        """MongoDB-based memory store"""
        
        def __init__(self, connection_string: str = "mongodb://localhost:27017/", database: str = "ollama_agents"):
            self.client = MongoClient(connection_string)
            self.db = self.client[database]
            self.collection = self.db['memories']
            self._create_indexes()
        
        def _create_indexes(self):
            """Create indexes for better performance"""
            self.collection.create_index([("agent_id", 1), ("key", 1)])
            self.collection.create_index([("expires_at", 1)])
            self.collection.create_index([("timestamp", -1)])
        
        def store(self, entry: MemoryEntry) -> None:
            doc = entry.to_dict()
            doc['_id'] = entry.id
            self.collection.replace_one({'_id': entry.id}, doc, upsert=True)
        
        def retrieve(self, agent_id: str, key: str) -> Optional[MemoryEntry]:
            doc = self.collection.find_one({
                'agent_id': agent_id,
                'key': key,
                '$or': [
                    {'expires_at': None},
                    {'expires_at': {'$gt': datetime.now().isoformat()}}
                ]
            })
            
            if doc:
                return MemoryEntry(
                    id=doc['_id'],
                    agent_id=doc['agent_id'],
                    key=doc['key'],
                    value=doc['value'],
                    timestamp=datetime.fromisoformat(doc['timestamp']),
                    metadata=doc.get('metadata', {}),
                    expires_at=datetime.fromisoformat(doc['expires_at']) if doc.get('expires_at') else None
                )
            return None
        
        def retrieve_all(self, agent_id: str, limit: Optional[int] = None) -> List[MemoryEntry]:
            query = {
                'agent_id': agent_id,
                '$or': [
                    {'expires_at': None},
                    {'expires_at': {'$gt': datetime.now().isoformat()}}
                ]
            }
            
            cursor = self.collection.find(query).sort('timestamp', -1)
            if limit:
                cursor = cursor.limit(limit)
            
            return [
                MemoryEntry(
                    id=doc['_id'],
                    agent_id=doc['agent_id'],
                    key=doc['key'],
                    value=doc['value'],
                    timestamp=datetime.fromisoformat(doc['timestamp']),
                    metadata=doc.get('metadata', {}),
                    expires_at=datetime.fromisoformat(doc['expires_at']) if doc.get('expires_at') else None
                )
                for doc in cursor
            ]
        
        def delete(self, agent_id: str, key: str) -> None:
            self.collection.delete_one({'agent_id': agent_id, 'key': key})
        
        def clear(self, agent_id: str) -> None:
            self.collection.delete_many({'agent_id': agent_id})
        
        def search(self, agent_id: str, query: str, limit: int = 10) -> List[MemoryEntry]:
            """Full-text search in MongoDB"""
            results = self.collection.find({
                'agent_id': agent_id,
                '$text': {'$search': query}
            }).limit(limit)
            
            return [
                MemoryEntry(
                    id=doc['_id'],
                    agent_id=doc['agent_id'],
                    key=doc['key'],
                    value=doc['value'],
                    timestamp=datetime.fromisoformat(doc['timestamp']),
                    metadata=doc.get('metadata', {}),
                    expires_at=datetime.fromisoformat(doc['expires_at']) if doc.get('expires_at') else None
                )
                for doc in results
            ]


# JSON File Memory Store
class JSONFileMemoryStore(MemoryStore):
    """JSON file-based memory store - simple, portable"""
    
    def __init__(self, file_path: str = "agent_memory.json"):
        self.file_path = file_path
        self._lock = threading.Lock()
        self._load()
    
    def _load(self):
        """Load memories from file"""
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                self._memories = data
        except (FileNotFoundError, json.JSONDecodeError):
            self._memories = {}
    
    def _save(self):
        """Save memories to file"""
        with open(self.file_path, 'w') as f:
            json.dump(self._memories, f, indent=2, default=str)
    
    def store(self, entry: MemoryEntry) -> None:
        with self._lock:
            if entry.agent_id not in self._memories:
                self._memories[entry.agent_id] = {}
            
            self._memories[entry.agent_id][entry.key] = entry.to_dict()
            self._save()
    
    def retrieve(self, agent_id: str, key: str) -> Optional[MemoryEntry]:
        with self._lock:
            if agent_id not in self._memories:
                return None
            
            data = self._memories[agent_id].get(key)
            if not data:
                return None
            
            # Check expiration
            if data.get('expires_at'):
                expires_at = datetime.fromisoformat(data['expires_at'])
                if datetime.now() > expires_at:
                    del self._memories[agent_id][key]
                    self._save()
                    return None
            
            return MemoryEntry(
                id=data['id'],
                agent_id=data['agent_id'],
                key=data['key'],
                value=data['value'],
                timestamp=datetime.fromisoformat(data['timestamp']),
                metadata=data.get('metadata', {}),
                expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
            )
    
    def retrieve_all(self, agent_id: str, limit: Optional[int] = None) -> List[MemoryEntry]:
        with self._lock:
            if agent_id not in self._memories:
                return []
            
            entries = []
            for key, data in self._memories[agent_id].items():
                # Check expiration
                if data.get('expires_at'):
                    expires_at = datetime.fromisoformat(data['expires_at'])
                    if datetime.now() > expires_at:
                        continue
                
                entries.append(MemoryEntry(
                    id=data['id'],
                    agent_id=data['agent_id'],
                    key=data['key'],
                    value=data['value'],
                    timestamp=datetime.fromisoformat(data['timestamp']),
                    metadata=data.get('metadata', {}),
                    expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
                ))
            
            # Sort by timestamp
            entries.sort(key=lambda x: x.timestamp, reverse=True)
            
            if limit:
                entries = entries[:limit]
            
            return entries
    
    def delete(self, agent_id: str, key: str) -> None:
        with self._lock:
            if agent_id in self._memories and key in self._memories[agent_id]:
                del self._memories[agent_id][key]
                self._save()
    
    def clear(self, agent_id: str) -> None:
        with self._lock:
            if agent_id in self._memories:
                del self._memories[agent_id]
                self._save()
    
    def search(self, agent_id: str, query: str, limit: int = 10) -> List[MemoryEntry]:
        """Simple keyword search"""
        entries = self.retrieve_all(agent_id)
        query_lower = query.lower()
        
        # Filter entries containing query
        matching = [
            e for e in entries
            if query_lower in str(e.value).lower() or query_lower in str(e.metadata).lower()
        ]
        
        return matching[:limit]


# Export new backends
__all__ = [
    'MemoryEntry',
    'MemoryStore',
    'InMemoryStore',
    'SQLiteMemoryStore',
    'RedisMemoryStore',
    'PostgresMemoryStore',
    'MongoDBMemoryStore',
    'JSONFileMemoryStore',
    'MemoryManager',
    'get_memory_manager',
    'set_memory_manager',
]
