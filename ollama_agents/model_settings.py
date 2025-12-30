"""
Model settings configuration following OpenAI agents patterns with Ollama-specific options
"""
from dataclasses import dataclass, field
from typing import Optional, Union, List, Dict, Any, Sequence
from enum import Enum
from .thinking import ThinkingMode


class TruncationStrategy(Enum):
    """Truncation strategies for handling long inputs"""
    AUTO = "auto"
    DISABLED = "disabled"


@dataclass
class ModelSettings:
    """
    Model settings configuration following OpenAI agents patterns with Ollama-specific options.
    
    This class provides a unified interface for configuring LLM parameters across different providers,
    with special handling for Ollama-specific options.
    """
    
    # Generation Control
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_tokens: Optional[int] = None
    verbosity: Optional[str] = None  # "low", "medium", "high"
    
    # Sampling Penalties
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    
    # Tool Integration
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    parallel_tool_calls: Optional[bool] = None
    
    # Reasoning and Thinking
    thinking_mode: Optional[ThinkingMode] = None
    
    # Advanced Ollama-specific options
    numa: Optional[bool] = None
    num_ctx: Optional[int] = None
    num_batch: Optional[int] = None
    num_gpu: Optional[int] = None
    main_gpu: Optional[int] = None
    low_vram: Optional[bool] = None
    f16_kv: Optional[bool] = None
    logits_all: Optional[bool] = None
    vocab_only: Optional[bool] = None
    use_mmap: Optional[bool] = None
    use_mlock: Optional[bool] = None
    embedding_only: Optional[bool] = None
    num_thread: Optional[int] = None
    num_keep: Optional[int] = None
    seed: Optional[int] = None
    num_predict: Optional[int] = None
    top_k: Optional[int] = None
    tfs_z: Optional[float] = None
    typical_p: Optional[float] = None
    repeat_last_n: Optional[int] = None
    repeat_penalty: Optional[float] = None
    mirostat: Optional[int] = None
    mirostat_tau: Optional[float] = None
    mirostat_eta: Optional[float] = None
    penalize_newline: Optional[bool] = None
    stop: Optional[Sequence[str]] = None
    
    # Response Control
    top_logprobs: Optional[int] = None
    include_usage: Optional[bool] = None
    
    # Advanced Features
    reasoning: Optional[Dict[str, Any]] = None
    prompt_cache_retention: Optional[str] = None  # "in_memory", "24h"
    truncation: Optional[TruncationStrategy] = None
    
    # Metadata & Storage
    metadata: Optional[Dict[str, str]] = None
    store: Optional[bool] = None
    
    # Extra parameters for flexibility
    extra_query: Optional[Dict[str, Any]] = None
    extra_body: Optional[Dict[str, Any]] = None
    extra_headers: Optional[Dict[str, str]] = None
    extra_args: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    def resolve(self, override: Optional['ModelSettings'] = None) -> 'ModelSettings':
        """
        Merge settings by overlaying non-None values from an override.
        
        Args:
            override: Optional ModelSettings to overlay on top of this instance
            
        Returns:
            A new ModelSettings instance with merged values
        """
        if override is None:
            return ModelSettings(**{k: v for k, v in self.__dict__.items() if v is not None})
        
        # Start with the current settings
        merged_values = self.__dict__.copy()
        
        # Overlay non-None values from override
        for key, value in override.__dict__.items():
            if value is not None:
                if key == 'extra_args':
                    # Special handling for extra_args: merge dictionaries
                    merged_values[key] = {**merged_values.get(key, {}), **value}
                else:
                    merged_values[key] = value
        
        # Create new instance with merged values, filtering out None values
        non_none_values = {k: v for k, v in merged_values.items() if v is not None}
        return ModelSettings(**non_none_values)
    
    def to_ollama_options(self) -> Dict[str, Any]:
        """
        Convert ModelSettings to Ollama-compatible options dictionary.
        
        Returns:
            Dictionary of options compatible with Ollama API
        """
        options = {}
        
        # Standard generation parameters
        if self.temperature is not None:
            options['temperature'] = self.temperature
        if self.top_p is not None:
            options['top_p'] = self.top_p
        if self.max_tokens is not None:
            options['num_predict'] = self.max_tokens  # Ollama uses num_predict
        if self.num_predict is not None:
            options['num_predict'] = self.num_predict
        
        # Sampling penalties
        if self.frequency_penalty is not None:
            options['frequency_penalty'] = self.frequency_penalty
        if self.presence_penalty is not None:
            options['presence_penalty'] = self.presence_penalty
        
        # Ollama-specific parameters
        if self.numa is not None:
            options['numa'] = self.numa
        if self.num_ctx is not None:
            options['num_ctx'] = self.num_ctx
        if self.num_batch is not None:
            options['num_batch'] = self.num_batch
        if self.num_gpu is not None:
            options['num_gpu'] = self.num_gpu
        if self.main_gpu is not None:
            options['main_gpu'] = self.main_gpu
        if self.low_vram is not None:
            options['low_vram'] = self.low_vram
        if self.f16_kv is not None:
            options['f16_kv'] = self.f16_kv
        if self.logits_all is not None:
            options['logits_all'] = self.logits_all
        if self.vocab_only is not None:
            options['vocab_only'] = self.vocab_only
        if self.use_mmap is not None:
            options['use_mmap'] = self.use_mmap
        if self.use_mlock is not None:
            options['use_mlock'] = self.use_mlock
        if self.embedding_only is not None:
            options['embedding_only'] = self.embedding_only
        if self.num_thread is not None:
            options['num_thread'] = self.num_thread
        if self.num_keep is not None:
            options['num_keep'] = self.num_keep
        if self.seed is not None:
            options['seed'] = self.seed
        if self.top_k is not None:
            options['top_k'] = self.top_k
        if self.tfs_z is not None:
            options['tfs_z'] = self.tfs_z
        if self.typical_p is not None:
            options['typical_p'] = self.typical_p
        if self.repeat_last_n is not None:
            options['repeat_last_n'] = self.repeat_last_n
        if self.repeat_penalty is not None:
            options['repeat_penalty'] = self.repeat_penalty
        if self.mirostat is not None:
            options['mirostat'] = self.mirostat
        if self.mirostat_tau is not None:
            options['mirostat_tau'] = self.mirostat_tau
        if self.mirostat_eta is not None:
            options['mirostat_eta'] = self.mirostat_eta
        if self.penalize_newline is not None:
            options['penalize_newline'] = self.penalize_newline
        if self.stop is not None:
            options['stop'] = list(self.stop)
        
        # Add any extra arguments
        options.update(self.extra_args)
        
        return options


# Default model settings for common use cases
DEFAULT_SETTINGS = ModelSettings(
    temperature=0.7,
    top_p=0.9,
    max_tokens=2048
)

SIMPLE_CHAT_SETTINGS = ModelSettings(
    temperature=0.7,
    max_tokens=1024
)

CREATIVE_SETTINGS = ModelSettings(
    temperature=0.9,
    top_p=0.9,
    max_tokens=2048
)

PRECISE_SETTINGS = ModelSettings(
    temperature=0.3,
    top_p=0.1,
    max_tokens=1024
)