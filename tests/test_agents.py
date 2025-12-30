"""
Tests for the Ollama Agents SDK
"""
import pytest
from unittest.mock import Mock, patch
from ollama_agents import Agent, AgentHandoff, tool, ThinkingMode, ThinkingManager, ModelSettings


class TestAgent:
    """Tests for the Agent class"""

    def test_agent_initialization(self):
        """Test agent initialization with new constructor"""
        agent = Agent(name="test_agent", model="llama3.2", instructions="Test instructions")

        assert agent.name == "test_agent"
        assert agent.model == "llama3.2"
        assert agent.instructions == "Test instructions"
        assert len(agent.messages) == 1
        assert agent.messages[0]["role"] == "system"
        assert agent.messages[0]["content"] == "Test instructions"

    def test_agent_add_message(self):
        """Test adding messages to agent"""
        agent = Agent(name="test_agent")
        agent.add_message("user", "Hello")
        # With no system prompt, messages is now 1
        assert len(agent.messages) == 1
        assert agent.messages[0]["role"] == "user"
        assert agent.messages[0]["content"] == "Hello"

    def test_thinking_mode_setting(self):
        """Test setting thinking mode"""
        settings = ModelSettings(thinking_mode=ThinkingMode.LOW)
        agent = Agent(name="test_agent", settings=settings)

        assert agent.settings.thinking_mode == ThinkingMode.LOW

        agent.set_thinking_mode(ThinkingMode.HIGH)
        assert agent.settings.thinking_mode == ThinkingMode.HIGH

    def test_agent_reset_conversation(self):
        """Test resetting conversation history"""
        agent = Agent(name="test_agent", instructions="Test instructions")

        agent.add_message("user", "Hello")
        agent.add_message("assistant", "Hi there!")

        assert len(agent.messages) == 3  # System + 2 messages

        agent.reset_conversation()
        assert len(agent.messages) == 1  # Just system message
        assert agent.messages[0]["role"] == "system"

    @pytest.mark.asyncio
    async def test_async_chat_method(self):
        """Test async chat method"""
        agent = Agent(name="test_agent")

        # Mock the async client
        mock_response = Mock()
        mock_response.message.content = "Test response"
        mock_response.prompt_eval_count = 0
        mock_response.eval_count = 0
        # mock_response.message.tool_calls = None
        # In python 3.8, you can't mock attributes that don't exist on the object.
        # Instead of `mock_response.message.tool_calls = None`, we do:
        type(mock_response.message).tool_calls = None


        with patch.object(agent.async_client, 'chat', return_value=mock_response):
            result = await agent.achat("Test message")
            assert result["content"] == "Test response"
            assert "raw_response" in result
    
    def test_handoff_initialization(self):
        """Test that handoff_manager is created when handoffs are provided"""
        french_agent = Agent(name="french_agent")
        spanish_agent = Agent(name="spanish_agent")
        triage_agent = Agent(
            name="triage_agent",
            instructions="Handoff to the appropriate agent.",
            handoffs=[french_agent, spanish_agent],
        )

        assert triage_agent.handoff_manager is not None
        assert isinstance(triage_agent.handoff_manager, AgentHandoff)
        assert "french_agent" in triage_agent.handoff_manager.agents
        assert "spanish_agent" in triage_agent.handoff_manager.agents
        assert "triage_agent" in triage_agent.handoff_manager.agents
        assert triage_agent.handoff_manager.current_agent_id == "triage_agent"


class TestThinkingManager:
    """Tests for the ThinkingManager class"""

    def test_thinking_manager_initialization(self):
        """Test ThinkingManager initialization"""
        tm = ThinkingManager()

        assert ThinkingMode.NONE in tm.mode_configs
        assert ThinkingMode.LOW in tm.mode_configs
        assert ThinkingMode.MEDIUM in tm.mode_configs
        assert ThinkingMode.HIGH in tm.mode_configs

    def test_get_config_for_mode(self):
        """Test getting configuration for a specific mode"""
        tm = ThinkingManager()

        config = tm.get_config_for_mode(ThinkingMode.MEDIUM)
        assert "description" in config
        assert "options" in config

    def test_apply_mode_to_options(self):
        """Test applying mode configuration to options"""
        tm = ThinkingManager()

        base_options = {"temperature": 0.8}
        result = tm.apply_mode_to_options(ThinkingMode.LOW, base_options)

        assert result["temperature"] == 0.8
        assert "num_predict" in result

        result2 = tm.apply_mode_to_options(ThinkingMode.HIGH, {})
        assert "num_predict" in result2
        assert "temperature" in result2


class TestToolRegistry:
    """Tests for the ToolRegistry class"""

    def test_tool_registration(self):
        """Test registering tools"""
        from ollama_agents.tools import ToolRegistry

        def sample_tool(x: int, y: str) -> str:
            """A sample tool for testing"""
            return f"{x}: {y}"

        registry = ToolRegistry()
        registry.register_tool(sample_tool)

        assert "sample_tool" in registry.tools
        assert registry.tools["sample_tool"] == sample_tool

    def test_get_ollama_tools(self):
        """Test getting tools in Ollama format"""
        from ollama_agents.tools import ToolRegistry

        def sample_tool(x: int, y: str) -> str:
            """
            A sample tool for testing.
            
            Args:
                x: An integer parameter
                y: A string parameter
            """
            return f"{x}: {y}"

        registry = ToolRegistry()
        registry.register_tool(sample_tool)

        ollama_tools = registry.get_ollama_tools()

        assert len(ollama_tools) == 1
        tool_def = ollama_tools[0]

        assert tool_def["type"] == "function"
        assert tool_def["function"]["name"] == "sample_tool"
        assert "A sample tool for testing." in tool_def["function"]["description"]

        params = tool_def["function"]["parameters"]
        assert "x" in params["properties"]
        assert "y" in params["properties"]
        assert params["properties"]["x"]["type"] == "integer"
        assert params["properties"]["y"]["type"] == "string"
        assert "x" in params["required"]
        assert "y" in params["required"]

    def test_tool_execution(self):
        """Test executing registered tools"""
        from ollama_agents.tools import ToolRegistry

        def sample_tool(x: int, y: str) -> str:
            return f"{x}: {y}"

        registry = ToolRegistry()
        registry.register_tool(sample_tool)

        result = registry.execute_tool("sample_tool", {"x": 42, "y": "hello"})
        assert result == "42: hello"


class TestAgentHandoff:
    """Tests for the AgentHandoff class"""

    def test_handoff_initialization(self):
        """Test handoff manager initialization"""
        agent1 = Agent(name="agent1")
        agent2 = Agent(name="agent2")

        handoff_manager = AgentHandoff({
            "agent1": agent1,
            "agent2": agent2
        })

        assert len(handoff_manager.agents) == 2
        assert handoff_manager.current_agent_id is None

    def test_set_and_get_current_agent(self):
        """Test setting and getting current agent"""
        agent1 = Agent(name="agent1")
        agent2 = Agent(name="agent2")

        handoff_manager = AgentHandoff({
            "agent1": agent1,
            "agent2": agent2
        })

        handoff_manager.set_current_agent("agent1")
        current_agent = handoff_manager.get_current_agent()

        assert current_agent is agent1

        with pytest.raises(ValueError):
            handoff_manager.set_current_agent("nonexistent")

    def test_handoff_to(self):
        """Test handoff to another agent"""
        agent1 = Agent(name="agent1", instructions="Agent 1")
        agent2 = Agent(name="agent2", instructions="Agent 2")

        handoff_manager = AgentHandoff({
            "agent1": agent1,
            "agent2": agent2
        })

        handoff_manager.set_current_agent("agent1")
        agent1.add_message("user", "Hello from user")

        result = handoff_manager.handoff_to("agent2", context={"reason": "transfer"})

        assert result["message"] == "Handoff completed to agent 'agent2'"
        assert handoff_manager.current_agent_id == "agent2"
        assert any("Context from previous agent" in msg["content"] for msg in agent2.messages)
        assert any(msg["content"] == "Hello from user" for msg in agent2.messages)

    def test_add_handoff_rule(self):
        """Test adding handoff rules"""
        agent1 = Agent(name="agent1")
        agent2 = Agent(name="agent2")

        handoff_manager = AgentHandoff({
            "agent1": agent1,
            "agent2": agent2
        })

        handoff_manager.add_handoff_rule(
            lambda msg: "math" in msg.lower(),
            "agent2",
            priority=1
        )

        assert len(handoff_manager.handoff_rules) == 1
        rule = handoff_manager.handoff_rules[0]
        assert rule["target_agent_id"] == "agent2"
        assert rule["priority"] == 1

    def test_check_handoff_rules(self):
        """Test checking handoff rules"""
        agent1 = Agent(name="agent1")
        agent2 = Agent(name="agent2")

        handoff_manager = AgentHandoff({
            "agent1": agent1,
            "agent2": agent2
        })

        handoff_manager.add_handoff_rule(
            lambda msg: "math" in msg.lower(),
            "agent2",
            priority=1
        )

        target = handoff_manager.check_handoff_rules("I need help with math")
        assert target == "agent2"

        target = handoff_manager.check_handoff_rules("I need help with writing")
        assert target is None


def test_tool_decorator():
    """Test the tool decorator"""
    @tool("A test tool")
    def test_function(x: int) -> int:
        """Original docstring"""
        return x * 2

    assert test_function(5) == 10
    assert "A test tool" in test_function.__doc__
    assert "Original docstring" in test_function.__doc__


if __name__ == "__main__":
    pytest.main([__file__])