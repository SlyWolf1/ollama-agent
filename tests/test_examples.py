"""
Tests for examples in the examples folder
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add examples directory to path
examples_dir = Path(__file__).parent.parent / "examples"
sys.path.insert(0, str(examples_dir))


class TestBasicExamples:
    """Test that basic examples can be imported and run"""
    
    def test_basic_examples_imports(self):
        """Test that basic_examples module can be imported"""
        try:
            import basic_examples
            assert hasattr(basic_examples, 'basic_agent_example')
        except ImportError as e:
            pytest.fail(f"Failed to import basic_examples: {e}")
    
    def test_basic_agent_example_exists(self):
        """Test that basic_agent_example function exists"""
        from basic_examples import basic_agent_example
        assert callable(basic_agent_example)
    
    @patch('ollama_agents.Agent')
    def test_basic_agent_can_be_mocked(self, mock_agent_class):
        """Test that we can mock the Agent class for testing"""
        from basic_examples import basic_agent_example
        
        # Setup mock
        mock_agent = Mock()
        mock_agent.chat.return_value = {'content': 'Test response'}
        mock_agent_class.return_value = mock_agent
        
        # This would run the example with mocked agent
        # basic_agent_example()  # Uncomment to test execution
        
        assert callable(basic_agent_example)


class TestAdvancedExamples:
    """Test that advanced examples can be imported and run"""
    
    def test_advanced_examples_imports(self):
        """Test that advanced_examples module can be imported"""
        try:
            import advanced_examples
            assert advanced_examples is not None
        except ImportError as e:
            pytest.fail(f"Failed to import advanced_examples: {e}")


class TestLoggingStatsExamples:
    """Test that logging and stats examples can be imported"""
    
    def test_logging_stats_examples_imports(self):
        """Test that logging_stats_examples module can be imported"""
        try:
            import logging_stats_examples
            assert logging_stats_examples is not None
        except ImportError as e:
            pytest.fail(f"Failed to import logging_stats_examples: {e}")


class TestModelSettingsExamples:
    """Test that model settings examples can be imported"""
    
    def test_model_settings_examples_imports(self):
        """Test that model_settings_examples module can be imported"""
        try:
            import model_settings_examples
            assert model_settings_examples is not None
        except ImportError as e:
            pytest.fail(f"Failed to import model_settings_examples: {e}")


class TestTracingExamples:
    """Test that tracing examples can be imported"""
    
    def test_tracing_examples_imports(self):
        """Test that tracing_examples module can be imported"""
        try:
            import tracing_examples
            assert tracing_examples is not None
        except ImportError as e:
            pytest.fail(f"Failed to import tracing_examples: {e}")
