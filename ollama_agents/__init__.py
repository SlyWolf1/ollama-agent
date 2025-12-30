"""
Ollama Agents SDK - Advanced agent framework with handoffs, tool calling, and thinking modes
"""
from .agent import Agent
from .handoff import AgentHandoff
from .tools import ToolRegistry, tool
from .thinking import ThinkingMode, ThinkingManager
from .tracing import TraceLevel, Tracer, get_tracer, set_global_tracing_level, start_global_trace_session, end_global_trace_session
from .model_settings import ModelSettings, DEFAULT_SETTINGS, SIMPLE_CHAT_SETTINGS, CREATIVE_SETTINGS, PRECISE_SETTINGS
from .utils import create_agent_with_settings, merge_settings, create_specialized_agent, AgentSession
from .stats import StatsTracker, TokenUsage, get_stats_tracker, StatType, enable_stats, disable_stats
from .logger import RichLogger as Logger, get_logger, set_global_log_level, LogLevel
from .mcp import MCPContext, MCPContextManager, MCPResource, MCPResourceType, MCPToolAdapter
from .context_manager import ContextManager, TruncationStrategy
from .caching import ResponseCache, CacheStrategy, enable_caching, disable_caching, get_cache
from .retry import RetryConfig, with_retry, async_with_retry, set_global_retry_config, get_retry_config, disable_retry
from .web_search import WebSearchTool, SearchProvider, SearchConfig, enable_web_search, create_web_search_agent
from .memory import MemoryManager, MemoryStore, SQLiteMemoryStore, RedisMemoryStore, PostgresMemoryStore, InMemoryStore, get_memory_manager, set_memory_manager

# Create AgentConfig alias for backward compatibility
AgentConfig = Agent

__version__ = "0.1.0"
__all__ = ["Agent", "AgentConfig", "AgentHandoff", "ToolRegistry", "tool", "ThinkingMode", "ThinkingManager",
           "TraceLevel", "Tracer", "get_tracer", "set_global_tracing_level",
           "start_global_trace_session", "end_global_trace_session",
           "ModelSettings", "DEFAULT_SETTINGS", "SIMPLE_CHAT_SETTINGS", "CREATIVE_SETTINGS", "PRECISE_SETTINGS",
           "create_agent_with_settings", "merge_settings", "create_specialized_agent", "AgentSession",
           "StatsTracker", "TokenUsage", "get_stats_tracker", "StatType", "enable_stats", "disable_stats",
           "Logger", "get_logger", "set_global_log_level", "LogLevel",
           "MCPContext", "MCPContextManager", "MCPResource", "MCPResourceType", "MCPToolAdapter",
           "ContextManager", "TruncationStrategy",
           "ResponseCache", "CacheStrategy", "enable_caching", "disable_caching", "get_cache",
           "RetryConfig", "with_retry", "async_with_retry", "set_global_retry_config", "get_retry_config", "disable_retry",
           "WebSearchTool", "SearchProvider", "SearchConfig", "enable_web_search", "create_web_search_agent",
           "MemoryManager", "MemoryStore", "SQLiteMemoryStore", "RedisMemoryStore", "PostgresMemoryStore", "InMemoryStore",
           "get_memory_manager", "set_memory_manager"]