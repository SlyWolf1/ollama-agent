"""
Thinking modes for Ollama agents
"""
from enum import Enum
from typing import Dict, Any


class ThinkingMode(Enum):
    """Different levels of thinking for Ollama agents"""
    NONE = None        # No enhanced thinking
    LOW = "low"        # Basic thinking
    MEDIUM = "medium"  # Moderate thinking
    HIGH = "high"      # Deep thinking


class ThinkingManager:
    """Manages different thinking strategies and configurations"""

    def __init__(self):
        self.mode_configs: Dict[ThinkingMode, Dict[str, Any]] = {
            ThinkingMode.NONE: {
                "description": "No enhanced thinking applied",
                "options": {}
            },
            ThinkingMode.LOW: {
                "description": "Basic cognitive processing",
                "options": {
                    "num_predict": 100,
                    "temperature": 0.5
                }
            },
            ThinkingMode.MEDIUM: {
                "description": "Moderate cognitive processing with balanced reasoning",
                "options": {
                    "num_predict": 200,
                    "temperature": 0.7
                }
            },
            ThinkingMode.HIGH: {
                "description": "Deep cognitive processing with extensive reasoning",
                "options": {
                    "num_predict": 400,
                    "temperature": 0.9
                }
            }
        }

    def get_config_for_mode(self, mode: ThinkingMode) -> Dict[str, Any]:
        """Get configuration for a specific thinking mode"""
        return self.mode_configs.get(mode, self.mode_configs[ThinkingMode.NONE])

    def apply_mode_to_options(self, mode: ThinkingMode, options: Dict[str, Any]) -> Dict[str, Any]:
        """Apply thinking mode configuration to Ollama options"""
        mode_config = self.get_config_for_mode(mode)
        # Merge mode-specific options with provided options (provided options take precedence)
        final_options = {**mode_config["options"], **options}
        return final_options