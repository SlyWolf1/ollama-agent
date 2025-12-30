"""
Tests for the tracing functionality in Ollama Agents SDK
"""
import pytest
from unittest.mock import Mock, patch
from ollama_agents import Agent, AgentConfig, AgentHandoff, TraceLevel, get_tracer
from ollama_agents.tracing import Tracer, TraceStore, TraceEvent


class TestTracingModule:
    """Tests for the tracing module"""
    
    def test_trace_level_enum(self):
        """Test TraceLevel enum values"""
        assert TraceLevel.OFF.value == "off"
        assert TraceLevel.MINIMAL.value == "minimal"
        assert TraceLevel.STANDARD.value == "standard"
        assert TraceLevel.VERBOSE.value == "verbose"
    
    def test_trace_event_creation(self):
        """Test TraceEvent creation"""
        event = TraceEvent(
            event_type="test.event",
            agent_id="test_agent",
            data={"key": "value"}
        )
        
        assert event.event_type == "test.event"
        assert event.agent_id == "test_agent"
        assert event.data["key"] == "value"
        assert event.id is not None
        assert event.timestamp is not None
    
    def test_trace_store(self):
        """Test TraceStore functionality"""
        store = TraceStore()
        
        # Add an event
        event = TraceEvent(event_type="test", agent_id="agent1")
        store.add_event(event)
        
        # Get events
        events = store.get_events()
        assert len(events) == 1
        assert events[0].event_type == "test"
        
        # Clear events
        store.clear()
        assert len(store.get_events()) == 0
    
    def test_trace_store_session(self):
        """Test TraceStore session functionality"""
        store = TraceStore()
        
        # Start a session
        session_id = store.start_session()
        assert store.current_session_id == session_id
        
        # Add an event with session
        event = TraceEvent(event_type="test", agent_id="agent1")
        store.add_event(event)
        
        # Verify event has session ID
        events = store.get_events()
        assert len(events) == 1
        assert events[0].session_id == session_id
        
        # End session
        store.end_session()
        assert store.current_session_id is None
    
    def test_tracer_basic_functionality(self):
        """Test basic tracer functionality"""
        tracer = Tracer(level=TraceLevel.STANDARD)
        
        # Test setting level
        tracer.set_level(TraceLevel.VERBOSE)
        assert tracer.level == TraceLevel.VERBOSE
        
        # Test span creation
        with tracer.span("test.operation", agent_id="test_agent", data={"param": "value"}):
            pass  # Span should be created and added to store
        
        events = tracer.get_trace_store().get_events()
        assert len(events) == 1
        assert events[0].event_type == "test.operation"
        assert events[0].agent_id == "test_agent"
        assert events[0].data["param"] == "value"
        assert events[0].duration is not None
    
    def test_tracer_session_management(self):
        """Test tracer session management"""
        tracer = Tracer(level=TraceLevel.STANDARD)
        
        # Start session
        session_id = tracer.start_trace_session()
        assert tracer.store.current_session_id == session_id
        
        # Create an event in session
        with tracer.span("session.operation"):
            pass
        
        # End session
        tracer.end_trace_session()
        assert tracer.store.current_session_id is None
        
        # Verify event has session ID
        events = tracer.get_trace_store().get_events(session_id)
        assert len(events) == 1
        assert events[0].session_id == session_id
    
    def test_global_tracer(self):
        """Test global tracer functionality"""
        # Test getting global tracer
        tracer = get_tracer()
        assert isinstance(tracer, Tracer)
        
        # Test global session management
        session_id = start_global_trace_session()
        assert tracer.store.current_session_id == session_id
        
        end_global_trace_session()
        assert tracer.store.current_session_id is None


class TestAgentTracing:
    """Tests for agent tracing functionality"""
    
    def test_agent_tracing_initialization(self):
        """Test agent tracing initialization"""
        config = AgentConfig(trace_level=TraceLevel.VERBOSE)
        agent = Agent(config)
        
        assert agent.tracer is not None
        assert agent.tracer.level == TraceLevel.VERBOSE
    
    def test_agent_chat_tracing(self):
        """Test tracing in agent chat method"""
        config = AgentConfig(trace_level=TraceLevel.STANDARD)
        agent = Agent(config)
        
        # Mock the client response
        mock_response = Mock()
        mock_response.message.content = "Test response"
        mock_response.message.tool_calls = None
        
        with patch.object(agent.client, 'chat', return_value=mock_response):
            response = agent.chat("Test message")
        
        # Check that trace events were created
        events = agent.get_trace_store().get_events()
        assert len(events) >= 1  # Should have at least one span event
        
        # Find the chat span
        chat_events = [e for e in events if e.event_type == "agent.chat"]
        assert len(chat_events) == 1
        assert chat_events[0].data["message"] == "Test message"
        assert chat_events[0].data["has_tools"] is False
        assert chat_events[0].duration is not None
    
    def test_agent_generate_tracing(self):
        """Test tracing in agent generate method"""
        config = AgentConfig(trace_level=TraceLevel.STANDARD)
        agent = Agent(config)
        
        # Mock the client response
        mock_response = Mock()
        mock_response.response = "Generated text"
        
        with patch.object(agent.client, 'generate', return_value=mock_response):
            response = agent.generate("Test prompt")
        
        # Check that trace events were created
        events = agent.get_trace_store().get_events()
        gen_events = [e for e in events if e.event_type == "agent.generate"]
        assert len(gen_events) == 1
        assert gen_events[0].data["prompt_length"] == len("Test prompt")
        assert gen_events[0].duration is not None


class TestHandoffTracing:
    """Tests for handoff tracing functionality"""
    
    def test_handoff_tracing_initialization(self):
        """Test handoff manager tracing initialization"""
        agent1 = Agent(AgentConfig(model="qwen3-vl:2b-thinking-q8_0"))
        agent2 = Agent(AgentConfig(model="qwen3-vl:2b-thinking-q8_0"))
        
        handoff_manager = AgentHandoff({
            "agent1": agent1,
            "agent2": agent2
        })
        
        assert handoff_manager.tracer is not None
    
    def test_handoff_tracing(self):
        """Test tracing in handoff operations"""
        agent1 = Agent(AgentConfig(model="qwen3-vl:2b-thinking-q8_0"))
        agent2 = Agent(AgentConfig(model="qwen3-vl:2b-thinking-q8_0"))
        
        handoff_manager = AgentHandoff({
            "agent1": agent1,
            "agent2": agent2
        })
        
        # Perform a handoff
        result = handoff_manager.handoff_to("agent2", context={"reason": "test"})
        
        # Check trace events
        events = handoff_manager.get_trace_store().get_events()
        handoff_events = [e for e in events if e.event_type == "handoff.execute"]
        assert len(handoff_events) == 1
        assert handoff_events[0].data["target_agent_id"] == "agent2"
        assert handoff_events[0].data["has_context"] is True
        assert handoff_events[0].duration is not None
        
        completed_events = [e for e in events if e.event_type == "handoff.completed"]
        assert len(completed_events) == 1
        assert completed_events[0].data["to_agent"] == "agent2"
    
    def test_handoff_chat_tracing(self):
        """Test tracing in handoff chat operations"""
        agent1 = Agent(AgentConfig(model="qwen3-vl:2b-thinking-q8_0"))
        agent2 = Agent(AgentConfig(model="qwen3-vl:2b-thinking-q8_0"))
        
        handoff_manager = AgentHandoff({
            "agent1": agent1,
            "agent2": agent2
        })
        
        # Mock the agent response
        mock_response = Mock()
        mock_response.message.content = "Test response"
        mock_response.message.tool_calls = None
        
        with patch.object(agent1.client, 'chat', return_value=mock_response):
            handoff_manager.set_current_agent("agent1")
            response = handoff_manager.chat_with_current("Test message")
        
        # Check trace events
        events = handoff_manager.get_trace_store().get_events()
        chat_events = [e for e in events if e.event_type == "handoff.chat_with_current"]
        assert len(chat_events) == 1
        assert chat_events[0].data["message_length"] == len("Test message")


def test_tracing_disabled():
    """Test that tracing is disabled when level is OFF"""
    config = AgentConfig(trace_level=TraceLevel.OFF)
    agent = Agent(config)

    # Mock the client response
    mock_response = Mock()
    mock_response.message.content = "Test response"
    mock_response.message.tool_calls = None

    with patch.object(agent.client, 'chat', return_value=mock_response):
        response = agent.chat("Test message")

    # No trace events should be created when tracing is OFF
    events = agent.get_trace_store().get_events()
    # In OFF mode, spans shouldn't be created, so no events should be stored
    # during the chat operation
    chat_events = [e for e in events if e.event_type == "agent.chat"]
    assert len(chat_events) == 0


if __name__ == "__main__":
    pytest.main([__file__])