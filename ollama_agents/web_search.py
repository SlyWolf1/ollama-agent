"""
Web search functionality for Ollama Agents SDK
Based on: https://docs.ollama.com/capabilities/web-search
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class SearchProvider(Enum):
    """Supported search providers"""
    BRAVE = "brave"
    DUCKDUCKGO = "duckduckgo"
    SEARXNG = "searxng"


@dataclass
class SearchConfig:
    """Configuration for web search"""
    provider: SearchProvider = SearchProvider.BRAVE
    api_key: Optional[str] = None
    max_results: int = 5
    safe_search: bool = True
    time_filter: Optional[str] = None  # e.g., "day", "week", "month", "year"
    region: Optional[str] = None  # e.g., "us", "uk", "ca"
    
    def to_ollama_options(self) -> Dict[str, Any]:
        """Convert to Ollama options format"""
        options = {}
        
        # Add provider-specific options
        if self.api_key:
            options['web_search_api_key'] = self.api_key
        
        if self.max_results:
            options['web_search_max_results'] = self.max_results
        
        if self.safe_search is not None:
            options['web_search_safe_search'] = self.safe_search
        
        if self.time_filter:
            options['web_search_time_filter'] = self.time_filter
        
        if self.region:
            options['web_search_region'] = self.region
        
        return options


class WebSearchTool:
    """
    Web search tool for agents using Ollama's built-in web search capability.
    
    Ollama supports web search through model options when the model supports it.
    This tool enables agents to search the web for current information.
    """
    
    def __init__(self, config: Optional[SearchConfig] = None):
        """
        Initialize web search tool
        
        Args:
            config: Search configuration (provider, API key, etc.)
        """
        self.config = config or SearchConfig()
    
    def get_tool_definition(self) -> Dict[str, Any]:
        """
        Get the tool definition for Ollama
        
        Returns:
            Tool definition dict
        """
        return {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for current information, news, facts, and data. Use this when you need up-to-date information that may not be in your training data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    
    def enable_for_agent(self, agent) -> None:
        """
        Enable web search for an agent
        
        Args:
            agent: The agent to enable web search for
        """
        # Add web search options to agent's model settings
        search_options = self.config.to_ollama_options()
        
        # Update agent settings
        if not hasattr(agent.settings, 'options'):
            agent.settings.options = {}
        
        agent.settings.options.update(search_options)
        agent.settings.options['web_search'] = True
        
        # Add the web search tool
        agent.add_tool(self._search_function)
    
    def _search_function(self, query: str, max_results: int = 5) -> str:
        """
        Internal search function (called by agent)
        
        Note: The actual search is performed by Ollama when web_search is enabled.
        This is a placeholder that documents the interface.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            Search results (provided by Ollama)
        """
        return f"Searching for: {query} (max results: {max_results})"


def enable_web_search(
    agent,
    provider: SearchProvider = SearchProvider.BRAVE,
    api_key: Optional[str] = None,
    max_results: int = 5
) -> WebSearchTool:
    """
    Enable web search for an agent
    
    Args:
        agent: The agent to enable web search for
        provider: Search provider to use
        api_key: API key for the search provider (required for Brave)
        max_results: Maximum number of search results
        
    Returns:
        WebSearchTool instance
        
    Example:
        ```python
        from ollama_agents import Agent, enable_web_search
        
        agent = Agent(name="researcher", model="qwen2.5-coder:3b-instruct-q8_0")
        enable_web_search(agent, api_key="your_brave_api_key")
        
        response = agent.chat("What happened in tech news today?")
        ```
    """
    config = SearchConfig(
        provider=provider,
        api_key=api_key,
        max_results=max_results
    )
    
    tool = WebSearchTool(config)
    tool.enable_for_agent(agent)
    
    return tool


def create_web_search_agent(
    name: str,
    model: str = None,
    instructions: Optional[str] = None,
    search_provider: SearchProvider = SearchProvider.BRAVE,
    search_api_key: Optional[str] = None,
    **kwargs
):
    """
    Create an agent with web search enabled
    
    Args:
        name: Agent name
        model: Model to use (defaults to Agent's default if None)
        instructions: System instructions
        search_provider: Search provider
        search_api_key: API key for search provider
        **kwargs: Additional agent arguments
        
    Returns:
        Agent with web search enabled
        
    Example:
        ```python
        from ollama_agents import create_web_search_agent
        
        agent = create_web_search_agent(
            name="researcher",
            model="qwen2.5-coder:3b-instruct-q8_0",
            instructions="You are a research assistant with web search.",
            search_api_key="your_brave_api_key"
        )
        
        response = agent.chat("What's the latest on AI developments?")
        ```
    """
    from .agent import Agent
    
    # Create agent - only pass model if specified
    agent_kwargs = {
        'name': name,
        'instructions': instructions or "You are a helpful assistant with web search capabilities.",
        **kwargs
    }
    if model is not None:
        agent_kwargs['model'] = model
    
    agent = Agent(**agent_kwargs)
    
    # Enable web search
    enable_web_search(
        agent,
        provider=search_provider,
        api_key=search_api_key
    )
    
    return agent
