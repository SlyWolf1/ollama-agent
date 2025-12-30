"""
Basic import and functionality tests
"""
import pytest
from ollama_agents import Agent, AgentConfig, AgentHandoff, tool, ThinkingMode


def test_imports():
    """Test that all modules can be imported"""
    from ollama_agents import Agent, AgentConfig, AgentHandoff, tool, ThinkingMode
    
    assert Agent is not None
    assert AgentConfig is not None
    assert AgentHandoff is not None
    assert tool is not None
    assert ThinkingMode is not None


def test_thinking_mode_enum():
    """Test ThinkingMode enum values"""
    assert ThinkingMode.NONE.value is None
    assert ThinkingMode.LOW.value == "low"
    assert ThinkingMode.MEDIUM.value == "medium"
    assert ThinkingMode.HIGH.value == "high"


def test_agent_config_defaults():
    """Test Agent default values"""
    agent = Agent(name="test_agent")
    
    assert agent.model == "qwen2.5-coder:3b-instruct-q8_0"
    assert agent.instructions is None
    assert agent.temperature is None  # Not set by default
    assert agent.max_tokens is None
    assert agent.thinking_mode is None  # None by default - not all models support thinking
    assert len(agent.tools) == 0
    assert agent.host is None
    assert agent.stream is False
    assert agent.keep_alive is None


def test_agent_creation():
    """Test basic agent creation"""
    agent = Agent(name="test_agent", model="qwen2.5-coder:3b-instruct-q8_0", instructions="Test prompt")
    
    assert agent.model == "qwen2.5-coder:3b-instruct-q8_0"
    assert agent.instructions == "Test prompt"
    assert len(agent.messages) == 1  # System message
    assert agent.messages[0]["role"] == "system"


if __name__ == "__main__":
    test_imports()
    test_thinking_mode_enum()
    test_agent_config_defaults()
    test_agent_creation()
    print("All basic tests passed!")