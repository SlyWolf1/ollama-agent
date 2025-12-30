"""
Statistics and logging functionality for Ollama Agents SDK
"""
import time
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import logging


class StatType(Enum):
    """Types of statistics collected"""
    TOKENS_INPUT = "tokens_input"
    TOKENS_OUTPUT = "tokens_output"
    TOKENS_TOTAL = "tokens_total"
    TOOLS_CALLED = "tools_called"
    TOOLS_SUCCESS = "tools_success"
    TOOLS_FAILED = "tools_failed"
    REQUESTS_MADE = "requests_made"
    RESPONSE_TIME = "response_time"
    CONVERSATION_TURNS = "conversation_turns"
    AGENT_SWITCHES = "agent_switches"
    CACHE_HITS = "cache_hits"
    CACHE_MISSES = "cache_misses"


class NoOpStatsTracker:
    """No-op stats tracker for performance - does nothing"""
    def increment(self, *args, **kwargs):
        pass
    
    def get_stat(self, *args, **kwargs):
        return 0.0
    
    def get_all_stats(self, *args, **kwargs):
        return {}
    
    def get_records(self, *args, **kwargs):
        return []
    
    def reset(self, *args, **kwargs):
        pass
    
    def summary(self, *args, **kwargs):
        return {}
    
    def export_json(self, *args, **kwargs):
        return "{}"


@dataclass
class StatRecord:
    """A single statistical record"""
    stat_type: StatType
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)


class StatsTracker:
    """Tracks statistics for agents and operations"""
    
    def __init__(self):
        self._stats: Dict[StatType, float] = {}
        self._records: List[StatRecord] = []
        self._lock = threading.Lock()
        self._session_stats: Dict[str, Dict[StatType, float]] = {}
        
        # Initialize all stat types to 0
        for stat_type in StatType:
            self._stats[stat_type] = 0.0
    
    def increment(self, stat_type: StatType, value: float = 1.0, 
                  agent_id: Optional[str] = None, session_id: Optional[str] = None,
                  metadata: Optional[Dict[str, Any]] = None):
        """Increment a statistic by a given value"""
        with self._lock:
            self._stats[stat_type] += value
            
            # Add to session stats if session_id is provided
            if session_id:
                if session_id not in self._session_stats:
                    self._session_stats[session_id] = {}
                self._session_stats[session_id][stat_type] = \
                    self._session_stats[session_id].get(stat_type, 0.0) + value
            
            # Record the stat change
            record = StatRecord(
                stat_type=stat_type,
                value=value,
                agent_id=agent_id,
                session_id=session_id,
                metadata=metadata or {}
            )
            self._records.append(record)
    
    def set(self, stat_type: StatType, value: float,
            agent_id: Optional[str] = None, session_id: Optional[str] = None,
            metadata: Optional[Dict[str, Any]] = None):
        """Set a statistic to a specific value"""
        with self._lock:
            self._stats[stat_type] = value
            
            # Update session stats if session_id is provided
            if session_id:
                if session_id not in self._session_stats:
                    self._session_stats[session_id] = {}
                self._session_stats[session_id][stat_type] = value
            
            # Record the stat change
            record = StatRecord(
                stat_type=stat_type,
                value=value,
                agent_id=agent_id,
                session_id=session_id,
                metadata=metadata or {}
            )
            self._records.append(record)
    
    def get(self, stat_type: StatType) -> float:
        """Get the current value of a statistic"""
        with self._lock:
            return self._stats.get(stat_type, 0.0)
    
    def get_session_stats(self, session_id: str) -> Dict[StatType, float]:
        """Get statistics for a specific session"""
        with self._lock:
            return self._session_stats.get(session_id, {}).copy()
    
    def get_all_stats(self) -> Dict[StatType, float]:
        """Get all current statistics"""
        with self._lock:
            return self._stats.copy()
    
    def get_records(self) -> List[StatRecord]:
        """Get all stat records"""
        with self._lock:
            return self._records.copy()
    
    def reset(self):
        """Reset all statistics to zero"""
        with self._lock:
            for stat_type in StatType:
                self._stats[stat_type] = 0.0
            self._records.clear()
            self._session_stats.clear()
    
    def reset_session(self, session_id: str):
        """Reset statistics for a specific session"""
        with self._lock:
            if session_id in self._session_stats:
                del self._session_stats[session_id]
    
    def export_stats(self, session_id: Optional[str] = None) -> str:
        """Export statistics to JSON format"""
        with self._lock:
            if session_id:
                stats = self.get_session_stats(session_id)
            else:
                stats = self.get_all_stats()
            
            # Convert StatType enums to strings for JSON serialization
            json_stats = {}
            for stat_type, value in stats.items():
                json_stats[stat_type.value] = value
            
            return json.dumps(json_stats, indent=2, default=str)
    
    def export_records(self) -> str:
        """Export all stat records to JSON format"""
        with self._lock:
            records_data = []
            for record in self._records:
                record_dict = {
                    "stat_type": record.stat_type.value,
                    "value": record.value,
                    "timestamp": record.timestamp.isoformat(),
                    "agent_id": record.agent_id,
                    "session_id": record.session_id,
                    "metadata": record.metadata
                }
                records_data.append(record_dict)
            
            return json.dumps(records_data, indent=2, default=str)


class TokenUsage:
    """Tracks token usage for LLM operations"""
    
    def __init__(self):
        self.prompt_tokens: int = 0
        self.completion_tokens: int = 0
        self.total_tokens: int = 0
    
    def add_usage(self, prompt_tokens: int = 0, completion_tokens: int = 0):
        """Add token usage to the tracker"""
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens
        self.total_tokens = self.prompt_tokens + self.completion_tokens
    
    def reset(self):
        """Reset token usage to zero"""
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0
    
    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary format"""
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens
        }


# Global stats tracker instance - use NoOp by default for better performance
_global_stats_tracker = NoOpStatsTracker()
_stats_enabled = False


def get_stats_tracker():
    """Get the global stats tracker instance"""
    return _global_stats_tracker


def enable_stats():
    """Enable statistics tracking globally"""
    global _global_stats_tracker, _stats_enabled
    if not _stats_enabled:
        _global_stats_tracker = StatsTracker()
        _stats_enabled = True
    return _global_stats_tracker


def disable_stats():
    """Disable statistics tracking globally for better performance"""
    global _global_stats_tracker, _stats_enabled
    _global_stats_tracker = NoOpStatsTracker()
    _stats_enabled = False