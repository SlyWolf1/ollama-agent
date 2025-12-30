"""
Utility functions and patterns for Ollama Agents SDK
"""
from typing import Dict, Any, Optional, Callable
from .model_settings import (
    ModelSettings,
    DEFAULT_SETTINGS,
    SIMPLE_CHAT_SETTINGS,
    CREATIVE_SETTINGS,
    PRECISE_SETTINGS
)
from .agent import Agent


def create_agent_with_settings(name: str, model: str, settings: ModelSettings, **kwargs) -> Agent:
    """
    Create an agent with a name and specific model settings.
    
    Args:
        name: The name of the agent.
        model: The model name to use.
        settings: ModelSettings configuration.
        **kwargs: Additional Agent parameters.
        
    Returns:
        Configured Agent instance.
    """
    return Agent(name=name, model=model, settings=settings, **kwargs)


def merge_settings(base: ModelSettings, override: ModelSettings) -> ModelSettings:
    """
    Merge two ModelSettings objects, with override values taking precedence.
    
    Args:
        base: Base ModelSettings.
        override: Override ModelSettings with values to overlay.
        
    Returns:
        Merged ModelSettings.
    """
    return base.resolve(override)


def create_specialized_agent(name: str, agent_type: str, model: str = None, **kwargs) -> Agent:
    """
    Create a specialized agent based on common use cases.
    
    Args:
        name: The name of the agent.
        agent_type: Type of agent ("simple", "creative", "precise", "default").
        model: Model name to use. If None, uses the Agent's default model.
        **kwargs: Additional configuration options.
        
    Returns:
        Specialized Agent instance.
    """
    if agent_type == "simple":
        settings = SIMPLE_CHAT_SETTINGS
    elif agent_type == "creative":
        settings = CREATIVE_SETTINGS
    elif agent_type == "precise":
        settings = PRECISE_SETTINGS
    elif agent_type == "default":
        settings = DEFAULT_SETTINGS
    else:
        raise ValueError(f"Unknown agent type: {agent_type}. Use 'simple', 'creative', 'precise', or 'default'")

    # Pass model only if specified, otherwise let Agent use its default
    if model is not None:
        return Agent(name=name, model=model, settings=settings, **kwargs)
    else:
        return Agent(name=name, settings=settings, **kwargs)


class AgentSession:
    """
    A session manager for managing multiple agent interactions with shared context.
    """

    def __init__(self, agents: Dict[str, Agent]):
        self.agents = agents
        self.current_agent_id: Optional[str] = None
        self.context: Dict[str, Any] = {}

    def set_current_agent(self, agent_id: str):
        """Set the current active agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent '{agent_id}' not found in session")
        self.current_agent_id = agent_id

    def get_current_agent(self) -> Optional[Agent]:
        """Get the current active agent"""
        if self.current_agent_id is None:
            return None
        return self.agents.get(self.current_agent_id)

    def run_with_agent(self, agent_id: str, func: Callable[[Agent], Any]) -> Any:
        """Run a function with a specific agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent '{agent_id}' not found in session")

        agent = self.agents[agent_id]
        return func(agent)

    async def arun_with_agent(self, agent_id: str, func: Callable[[Agent], Any]) -> Any:
        """Asynchronously run a function with a specific agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent '{agent_id}' not found in session")

        agent = self.agents[agent_id]
        return await func(agent)

    def set_context(self, key: str, value: Any):
        """Set a value in the shared context"""
        self.context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a value from the shared context"""
        return self.context.get(key, default)

    def clear_context(self):
        """Clear the shared context"""
        self.context.clear()
