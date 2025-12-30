"""
Tracing functionality for Ollama Agents SDK with enhanced token and performance metrics
"""
import time
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from contextlib import contextmanager
import json


class TraceLevel(Enum):
    """Tracing levels for the Ollama Agents SDK"""
    OFF = "off"        # No tracing
    MINIMAL = "minimal"  # Basic tracing (start/end of operations)
    STANDARD = "standard"  # Standard tracing (messages, tool calls)
    VERBOSE = "verbose"  # Detailed tracing (all internal operations)


@dataclass
class TokenUsage:
    """Token usage information for tracing"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cache_read: int = 0  # Tokens read from cache
    cache_write: int = 0  # Tokens written to cache


@dataclass
class PerformanceMetrics:
    """Performance metrics for operations"""
    tokens_per_second: Optional[float] = None
    chars_per_second: Optional[float] = None
    response_time: Optional[float] = None
    processing_time: Optional[float] = None
    input_throughput: Optional[float] = None  # Tokens per second for input
    output_throughput: Optional[float] = None  # Tokens per second for output


@dataclass
class TraceEvent:
    """Represents a single trace event"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    level: TraceLevel = TraceLevel.STANDARD
    event_type: str = ""
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    parent_id: Optional[str] = None
    duration: Optional[float] = None
    token_usage: Optional[TokenUsage] = None
    performance: Optional[PerformanceMetrics] = None


class TraceStore:
    """Store for trace events"""
    
    def __init__(self):
        self.events: List[TraceEvent] = []
        self.current_session_id: Optional[str] = None
    
    def add_event(self, event: TraceEvent):
        """Add an event to the trace store"""
        if not event.session_id and self.current_session_id:
            event.session_id = self.current_session_id
        self.events.append(event)
    
    def get_events(self, session_id: Optional[str] = None) -> List[TraceEvent]:
        """Get events, optionally filtered by session"""
        if session_id:
            return [event for event in self.events if event.session_id == session_id]
        return self.events[:]
    
    def get_token_usage_summary(self, session_id: Optional[str] = None) -> TokenUsage:
        """Get total token usage for a session"""
        events = self.get_events(session_id)
        total_usage = TokenUsage()
        
        for event in events:
            if event.token_usage:
                total_usage.prompt_tokens += event.token_usage.prompt_tokens
                total_usage.completion_tokens += event.token_usage.completion_tokens
                total_usage.total_tokens += event.token_usage.total_tokens
                total_usage.cache_read += event.token_usage.cache_read
                total_usage.cache_write += event.token_usage.cache_write
        
        return total_usage
    
    def get_performance_summary(self, session_id: Optional[str] = None) -> Dict[str, float]:
        """Get performance summary for a session"""
        events = self.get_events(session_id)
        total_response_time = 0
        total_duration = 0
        total_input_tokens = 0
        total_output_tokens = 0
        event_count = 0
        
        for event in events:
            if event.duration:
                total_duration += event.duration
                event_count += 1
            if event.token_usage:
                total_input_tokens += event.token_usage.prompt_tokens
                total_output_tokens += event.token_usage.completion_tokens
            if event.performance and event.performance.response_time:
                total_response_time += event.performance.response_time
        
        summary = {}
        if event_count > 0:
            summary['avg_response_time'] = total_response_time / event_count
            summary['total_duration'] = total_duration
        if total_duration > 0:
            summary['input_tokens_per_second'] = total_input_tokens / total_duration
            summary['output_tokens_per_second'] = total_output_tokens / total_duration
            summary['total_tokens_per_second'] = (total_input_tokens + total_output_tokens) / total_duration
        
        return summary
    
    def clear(self):
        """Clear all events"""
        self.events.clear()
    
    def start_session(self) -> str:
        """Start a new tracing session"""
        self.current_session_id = str(uuid.uuid4())
        return self.current_session_id
    
    def end_session(self):
        """End the current tracing session"""
        self.current_session_id = None
    
    def export_to_json(self, session_id: Optional[str] = None) -> str:
        """Export trace events to JSON format"""
        events = self.get_events(session_id)
        export_data = []
        
        for event in events:
            event_dict = {
                "id": event.id,
                "timestamp": event.timestamp.isoformat(),
                "level": event.level.value,
                "event_type": event.event_type,
                "agent_id": event.agent_id,
                "session_id": event.session_id,
                "data": event.data,
                "parent_id": event.parent_id,
                "duration": event.duration
            }
            
            # Add token usage if present
            if event.token_usage:
                event_dict["token_usage"] = {
                    "prompt_tokens": event.token_usage.prompt_tokens,
                    "completion_tokens": event.token_usage.completion_tokens,
                    "total_tokens": event.token_usage.total_tokens,
                    "cache_read": event.token_usage.cache_read,
                    "cache_write": event.token_usage.cache_write
                }
            
            # Add performance metrics if present
            if event.performance:
                event_dict["performance"] = {
                    "tokens_per_second": event.performance.tokens_per_second,
                    "chars_per_second": event.performance.chars_per_second,
                    "response_time": event.performance.response_time,
                    "processing_time": event.performance.processing_time,
                    "input_throughput": event.performance.input_throughput,
                    "output_throughput": event.performance.output_throughput
                }
            
            export_data.append(event_dict)
        
        return json.dumps(export_data, indent=2)


class Tracer:
    """Main tracer class for the Ollama Agents SDK"""
    
    def __init__(self, level: TraceLevel = TraceLevel.STANDARD):
        self.level = level
        self.store = TraceStore()
        self.active_spans: List[TraceEvent] = []
    
    def set_level(self, level: TraceLevel):
        """Set the tracing level"""
        self.level = level
    
    def start_trace_session(self) -> str:
        """Start a new trace session"""
        return self.store.start_session()
    
    def end_trace_session(self):
        """End the current trace session"""
        self.store.end_session()
    
    @contextmanager
    def span(self, event_type: str, agent_id: Optional[str] = None, 
             data: Optional[Dict[str, Any]] = None, parent_id: Optional[str] = None,
             token_usage: Optional[TokenUsage] = None, 
             performance: Optional[PerformanceMetrics] = None):
        """Create a trace span using context manager"""
        # Quick exit for disabled tracing - no overhead
        if self.level == TraceLevel.OFF:
            yield None
            return
        
        start_time = time.time()
        span_id = str(uuid.uuid4())
        
        event = TraceEvent(
            id=span_id,
            event_type=event_type,
            agent_id=agent_id,
            data=data or {},
            parent_id=parent_id,
            token_usage=token_usage,
            performance=performance
        )
        
        self.active_spans.append(event)
        
        try:
            yield event
        finally:
            duration = time.time() - start_time
            event.duration = duration
            
            # Update performance metrics if not already set
            if event.performance is None:
                event.performance = PerformanceMetrics()
            if event.performance.response_time is None:
                event.performance.response_time = duration
            
            # Add the completed span to the store
            self.store.add_event(event)
            if self.active_spans and self.active_spans[-1].id == span_id:
                self.active_spans.pop()
    
    def log_event(self, event_type: str, agent_id: Optional[str] = None,
                  data: Optional[Dict[str, Any]] = None,
                  token_usage: Optional[TokenUsage] = None,
                  performance: Optional[PerformanceMetrics] = None):
        """Log a trace event"""
        if self.level == TraceLevel.OFF:
            return
        
        event = TraceEvent(
            event_type=event_type,
            agent_id=agent_id,
            data=data or {},
            token_usage=token_usage,
            performance=performance
        )
        
        self.store.add_event(event)
    
    def get_trace_store(self) -> TraceStore:
        """Get the trace store"""
        return self.store
    
    def export_session(self, session_id: Optional[str] = None) -> str:
        """Export the current session to JSON"""
        return self.store.export_to_json(session_id)
    
    def get_token_usage_summary(self, session_id: Optional[str] = None) -> TokenUsage:
        """Get token usage summary for a session"""
        return self.store.get_token_usage_summary(session_id)
    
    def get_performance_summary(self, session_id: Optional[str] = None) -> Dict[str, float]:
        """Get performance summary for a session"""
        return self.store.get_performance_summary(session_id)


# Global tracer instance
_global_tracer = Tracer()


def get_tracer() -> Tracer:
    """Get the global tracer instance"""
    return _global_tracer


def set_global_tracing_level(level: TraceLevel):
    """Set the global tracing level"""
    _global_tracer.set_level(level)


def start_global_trace_session() -> str:
    """Start a global trace session"""
    return _global_tracer.start_trace_session()


def end_global_trace_session():
    """End the global trace session"""
    _global_tracer.end_trace_session()