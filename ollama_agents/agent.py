"""
Core Agent class implementation with thinking modes, tool calling, and handoff capabilities
"""
from __future__ import annotations
import asyncio
import time
from typing import Any, Dict, List, Optional, Union, Callable, TYPE_CHECKING
from dataclasses import dataclass, field
import ollama
from .tools import ToolRegistry
from .thinking import ThinkingMode, ThinkingManager
from .tracing import get_tracer, TraceLevel
from .model_settings import ModelSettings, DEFAULT_SETTINGS
from .stats import get_stats_tracker, StatType, TokenUsage
from .context_manager import TruncationStrategy
from .caching import get_cache
from .retry import RetryConfig, with_retry, async_with_retry
from .memory import MemoryManager, get_memory_manager, MemoryStore, InMemoryStore

if TYPE_CHECKING:
    from .handoff import AgentHandoff
    from .caching import ResponseCache


@dataclass
class Agent:
    """
    Advanced Ollama Agent with thinking modes, tool calling, and handoff capabilities.
    Follows OpenAI Agents SDK and Ollama naming conventions.
    """
    name: str
    instructions: Optional[str] = None
    model: Optional[str] = 'qwen2.5-coder:3b-instruct-q8_0'
    tools: List[Callable] = field(default_factory=list)
    handoffs: List['Agent'] = field(default_factory=list)
    
    # Common parameters (matching OpenAI/Ollama conventions)
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_tokens: Optional[int] = None
    thinking_mode: Optional[ThinkingMode] = None  # None by default - not all models support thinking
    
    # Ollama-specific parameters
    host: Optional[str] = None
    stream: bool = False
    keep_alive: Union[float, str, None] = None
    timeout: int = 30
    options: Optional[Dict[str, Any]] = None  # Advanced Ollama options
    
    # Deprecated: Use direct parameters instead
    settings: Optional[ModelSettings] = None
    
    # Tracing and monitoring (disabled by default for performance)
    trace_level: TraceLevel = TraceLevel.OFF
    enable_tracing: bool = False
    
    # Advanced features
    max_context_length: int = 20000
    context_truncation_strategy: TruncationStrategy = TruncationStrategy.SUMMARIZE_MIDDLE
    enable_cache: bool = False
    cache: Optional[Any] = None
    enable_retry: bool = False
    retry_config: Optional[Any] = None

    # Memory features
    enable_memory: bool = False
    memory_store: Optional[MemoryStore] = None

    # Initialized in __post_init__
    client: ollama.Client = field(init=False, repr=False)
    async_client: ollama.AsyncClient = field(init=False, repr=False)
    tool_registry: ToolRegistry = field(init=False, repr=False)
    thinking_manager: ThinkingManager = field(init=False, repr=False)
    tracer: Any = field(init=False, repr=False)
    stats_tracker: Any = field(init=False, repr=False)
    token_usage: TokenUsage = field(init=False, repr=False)
    messages: List[Dict[str, str]] = field(init=False, repr=False)
    handoff_manager: Optional[AgentHandoff] = field(init=False, default=None, repr=False)
    summary_threshold: int = field(init=False, repr=False)
    memory_manager: MemoryManager = field(init=False, repr=False)

    def __post_init__(self):
        from .handoff import AgentHandoff

        # Merge direct parameters with settings (direct params take precedence)
        # Build effective settings from direct parameters or legacy settings
        if self.settings is None:
            # Create settings from direct parameters
            self.settings = ModelSettings(
                temperature=self.temperature,
                top_p=self.top_p,
                max_tokens=self.max_tokens,
                thinking_mode=self.thinking_mode
            )
        else:
            # Merge: direct parameters override settings
            if self.temperature is not None:
                self.settings.temperature = self.temperature
            if self.top_p is not None:
                self.settings.top_p = self.top_p
            if self.max_tokens is not None:
                self.settings.max_tokens = self.max_tokens
            if self.thinking_mode is not None:
                self.settings.thinking_mode = self.thinking_mode

        # If no settings at all, use defaults
        if self.settings is None:
            self.settings = DEFAULT_SETTINGS

        # Initialize clients
        self.client = ollama.Client(host=self.host, timeout=self.timeout)
        self.async_client = ollama.AsyncClient(host=self.host, timeout=self.timeout)

        # Initialize managers
        self.tool_registry = ToolRegistry()
        self.thinking_manager = ThinkingManager()

        # Initialize tracing
        self.tracer = get_tracer()
        if self.enable_tracing:
            self.tracer.set_level(self.trace_level)

        # Initialize stats tracking
        self.stats_tracker = get_stats_tracker()
        self.token_usage = TokenUsage()

        # Register tools
        for tool_func in self.tools:
            self.tool_registry.register_tool(tool_func)

        # Initialize conversation history
        self.messages = []
        if self.instructions:
            self.messages.append({"role": "system", "content": self.instructions})

        # Initialize handoff manager
        if self.handoffs:
            agents_dict = {agent.name: agent for agent in self.handoffs}
            agents_dict[self.name] = self
            self.handoff_manager = AgentHandoff(agents_dict)
            self.handoff_manager.set_current_agent(self.name)

        # Initialize cache if enabled
        if self.enable_cache and self.cache is None:
            # Use global cache if available, otherwise create new one
            from .caching import ResponseCache, CacheStrategy
            global_cache = get_cache()
            if global_cache:
                self.cache = global_cache
            else:
                self.cache = ResponseCache(max_size=1000, strategy=CacheStrategy.LRU)

        # Initialize retry config if enabled
        if self.enable_retry and self.retry_config is None:
            self.retry_config = RetryConfig()

        # Initialize memory manager if enabled
        if self.enable_memory:
            if self.memory_store is not None:
                self.memory_manager = MemoryManager(self.memory_store)
            else:
                # Use default memory manager
                self.memory_manager = get_memory_manager()
        else:
            # Use in-memory store for basic functionality without persistent memory
            self.memory_manager = MemoryManager(InMemoryStore())

        # Context management settings
        self.summary_threshold = int(self.max_context_length * 0.75)  # When to trigger summarization (75% of max)

    def should_summarize_context(self) -> bool:
        """Check if the current context should be summarized"""
        current_length = sum(len(msg.get("content", "")) for msg in self.messages)
        return current_length > self.summary_threshold

    def summarize_context(self) -> str:
        """Summarize the current conversation context"""
        if not self.messages:
            return ""

        # Create a summary prompt for the LLM to summarize the conversation
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in self.messages
            if msg['role'] in ['user', 'assistant']
        ])

        if len(conversation_text) < 100:  # If conversation is too short, no need to summarize
            return conversation_text

        # Use the model to generate a summary
        try:
            summary_prompt = f"Please provide a concise summary of the following conversation:\n\n{conversation_text}\n\nSummary:"
            summary_response = self.client.generate(
                model=self.model,
                prompt=summary_prompt,
                options={"num_predict": 200, "temperature": 0.3}
            )
            return summary_response.response
        except Exception:
            # If summarization fails, return a simple truncation
            return conversation_text[:1000] + "... [truncated]"

    def get_context_summary_message(self) -> Dict[str, str]:
        """Get a message containing the context summary"""
        summary = self.summarize_context()
        return {
            "role": "system",
            "content": f"Conversation summary: {summary}"
        }

    def add_tool(self, func: Callable):
        """Add a tool to the agent's tool registry"""
        self.tool_registry.register_tool(func)

    def set_thinking_mode(self, mode: ThinkingMode):
        """Set the agent's thinking mode"""
        self.settings.thinking_mode = mode

    def add_message(self, role: str, content: str):
        """Add a message to the conversation history"""
        self.messages.append({"role": role, "content": content})

    def _prepare_tools(self):
        """Prepare tools for Ollama API call"""
        return self.tool_registry.get_ollama_tools()

    def _get_think_param(self):
        """Get the appropriate think parameter based on thinking mode"""
        thinking_mode = self.settings.thinking_mode
        # Only return think parameter if explicitly set
        if thinking_mode is None:
            return None
        elif thinking_mode == ThinkingMode.NONE:
            return None
        elif thinking_mode == ThinkingMode.LOW:
            return "low"
        elif thinking_mode == ThinkingMode.MEDIUM:
            return "medium"
        elif thinking_mode == ThinkingMode.HIGH:
            return "high"
        else:
            return None

    def _get_options(self):
        """Get Ollama options based on configuration and thinking mode"""
        options = self.settings.to_ollama_options()
        # Only apply thinking mode if explicitly set
        if self.settings.thinking_mode:
            final_options = self.thinking_manager.apply_mode_to_options(self.settings.thinking_mode, options)
        else:
            final_options = options
        return final_options

    def chat(self, message: str, tools: Optional[List[Callable]] = None) -> Dict[str, Any]:
        """
        Send a message to the agent and get a response.
        Supports caching and retry.
        """
        from .logger import get_logger
        logger = get_logger()
        
        logger.info(f"💬 Agent {self.name} received chat message")
        logger.debug(f"   Message: {message[:100]}...")
        logger.debug(f"   Has handoff_manager: {self.handoff_manager is not None}")
        logger.debug(f"   Agent has {len(self.tool_registry.tools)} registered tools: {list(self.tool_registry.tools.keys())}")
        
        if self.handoff_manager:
            # If a handoff manager exists, check for handoff rules
            logger.debug(f"   Checking handoff rules...")
            target_agent_id = self.handoff_manager.check_handoff_rules(message)
            logger.debug(f"   Target agent from rules: {target_agent_id}")
            
            if target_agent_id and target_agent_id != self.name:
                logger.info(f"🔀 Handing off to agent: {target_agent_id}")
                return self.handoff_manager.handoff_to(target_agent_id, context={"trigger_message": message})

        start_time = time.time()

        with self.tracer.span("agent.chat", agent_id=self.name,
                             data={"message": message, "has_tools": bool(tools)}) as span:
            self.add_message("user", message)

            all_tools = self._prepare_tools()
            if tools:
                temp_registry = ToolRegistry()
                for tool_func in tools:
                    temp_registry.register_tool(tool_func)
                all_tools.extend(temp_registry.get_ollama_tools())

            self.stats_tracker.increment(StatType.TOOLS_CALLED, len(all_tools), agent_id=self.name)

            think_param = self._get_think_param()
            options = self._get_options()

            # # Check cache if enabled
            # if self.enable_cache and self.cache:
            #     cached_response = self.cache.get(
            #         message=message,
            #         model=self.model,
            #         options=options,
            #         tools=all_tools
            #     )
            #     if cached_response:
            #         self.stats_tracker.increment(StatType.CACHE_HITS, 1, agent_id=self.name)
            #         return cached_response

            self.stats_tracker.increment(StatType.REQUESTS_MADE, 1, agent_id=self.name)

            # # Make API call with retry if enabled
            # if self.enable_retry and self.retry_config:
            #     def on_retry_callback(exception, attempt):
            #         self.tracer.log(f"Retry attempt {attempt} after error: {exception}", agent_id=self.name)
                
            #     @with_retry(self.retry_config, on_retry=on_retry_callback)
            #     def make_request():
            #         return self.client.chat(
            #             model=self.model,
            #             messages=self.messages,
            #             tools=all_tools if all_tools else None,
            #             options=options,
            #             keep_alive=self.keep_alive,
            #             stream=self.stream,
            #             think=think_param
            #         )
                
            #     response = make_request()
            # else:
            # Build chat parameters
            logger.info(f"📤 Preparing API call to model: {self.model}")
            logger.debug(f"   Messages in history: {len(self.messages)}")
            logger.debug(f"   Tools available: {len(all_tools) if all_tools else 0}")
            logger.debug(f"   Think param: {think_param}")
            
            chat_params = {
                'model': self.model,
                'messages': self.messages,
                'tools': all_tools if all_tools else None,
                'stream': self.stream,
                'options': options if options else None,
                'keep_alive': self.keep_alive
            }
            
            # Only include think parameter if explicitly set
            if think_param is not None:
                chat_params['think'] = think_param
            
            logger.debug(f"   Calling ollama.chat...")
            response = self.client.chat(**chat_params)
            logger.info(f"📥 Received response from model")
            logger.debug(f"   Response content length: {len(response.message.content)} chars")
            logger.debug(f"   Response content preview: {response.message.content[:200]}...")

            response_time = time.time() - start_time
            self.stats_tracker.increment(StatType.RESPONSE_TIME, response_time, agent_id=self.name)

            if hasattr(response, 'prompt_eval_count') and response.prompt_eval_count:
                self.token_usage.add_usage(prompt_tokens=response.prompt_eval_count)
                self.stats_tracker.increment(StatType.TOKENS_INPUT, response.prompt_eval_count, agent_id=self.name)

            if hasattr(response, 'eval_count') and response.eval_count:
                self.token_usage.add_usage(completion_tokens=response.eval_count)
                self.stats_tracker.increment(StatType.TOKENS_OUTPUT, response.eval_count, agent_id=self.name)

            # Execute tool calls if present - loop until no more tool calls
            from .logger import get_logger
            import json
            import re
            logger = get_logger()
            
            max_iterations = 5  # Prevent infinite loops
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                logger.debug(f"🔄 Tool execution iteration {iteration}/{max_iterations}")
                
                logger.info(f"🔍 Checking for tool calls in response from {self.name}")
                logger.debug(f"   Has tool_calls attr: {hasattr(response.message, 'tool_calls')}")
                
                if hasattr(response.message, 'tool_calls'):
                    logger.debug(f"   tool_calls value: {response.message.tool_calls}")
                    logger.debug(f"   tool_calls is truthy: {bool(response.message.tool_calls)}")
                
                # Check for proper tool_calls first
                has_tool_calls = hasattr(response.message, 'tool_calls') and response.message.tool_calls
                
                # If no proper tool_calls, try to parse from content (fallback for models that don't support it)
                parsed_tool_calls = []
                if not has_tool_calls and response.message.content:
                    logger.debug(f"   No proper tool_calls, checking content for JSON tool calls...")
                    # Try to extract JSON from markdown code blocks or plain text
                    content = response.message.content.strip()
                    
                    # Remove markdown code blocks if present
                    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
                    if json_match:
                        content = json_match.group(1)
                        logger.debug(f"   Found JSON in markdown block")
                    
                    # Try to parse as JSON
                    try:
                        parsed = json.loads(content)
                        if isinstance(parsed, dict) and 'name' in parsed and 'arguments' in parsed:
                            logger.info(f"✅ Parsed tool call from content: {parsed['name']}")
                            # Create a fake tool_call object
                            class FakeToolCall:
                                class FakeFunction:
                                    def __init__(self, name, arguments):
                                        self.name = name
                                        self.arguments = arguments
                                def __init__(self, name, arguments):
                                    self.function = self.FakeFunction(name, arguments)
                            
                            parsed_tool_calls = [FakeToolCall(parsed['name'], parsed['arguments'])]
                            has_tool_calls = True
                            logger.info(f"✅ Created tool call from parsed content")
                    except json.JSONDecodeError:
                        logger.debug(f"   Content is not valid JSON")
                    except Exception as e:
                        logger.debug(f"   Error parsing content: {e}")
                
                if not has_tool_calls:
                    logger.info(f"ℹ️  No tool calls found in response from {self.name}")
                    break  # Exit loop - no more tool calls
                
                # Use parsed_tool_calls if we had to parse from content, otherwise use response.message.tool_calls
                tool_calls_to_execute = parsed_tool_calls if parsed_tool_calls else response.message.tool_calls
                
                logger.info(f"✅ Found {len(tool_calls_to_execute)} tool call(s) to execute")
                self.stats_tracker.increment(StatType.TOOLS_SUCCESS, len(tool_calls_to_execute), agent_id=self.name)
                
                # Add assistant's message with tool calls to history
                logger.debug(f"Adding assistant message to history: {response.message.content[:100]}...")
                self.add_message("assistant", response.message.content)
                
                # Execute each tool call
                for i, tool_call in enumerate(tool_calls_to_execute, 1):
                    tool_name = tool_call.function.name
                    tool_args = tool_call.function.arguments
                    
                    logger.info(f"🔧 Executing tool {i}/{len(tool_calls_to_execute)}: {tool_name}")
                    logger.debug(f"   Arguments: {tool_args}")
                    
                    self.tracer.log_event("tool.executing", agent_id=self.name, 
                                        data={"tool": tool_name, "args": tool_args})
                    
                    try:
                        # Execute the tool
                        logger.debug(f"   Calling {tool_name} from registry...")
                        tool_result = self.tool_registry.tools[tool_name](**tool_args)
                        logger.info(f"✅ Tool {tool_name} completed successfully")
                        logger.debug(f"   Result length: {len(str(tool_result))} chars")
                        logger.debug(f"   Result preview: {str(tool_result)[:200]}...")
                        
                        # Add tool result to conversation
                        self.messages.append({
                            "role": "tool",
                            "content": str(tool_result)
                        })
                        
                        logger.debug(f"   Added tool result to messages (role: tool)")
                        
                        self.tracer.log_event("tool.success", agent_id=self.name,
                                            data={"tool": tool_name, "result_length": len(str(tool_result))})
                    except Exception as e:
                        logger.error(f"❌ Tool {tool_name} failed: {str(e)}")
                        logger.error(f"   Exception type: {type(e).__name__}")
                        import traceback
                        logger.debug(f"   Traceback:\n{traceback.format_exc()}")
                        
                        error_msg = f"Tool {tool_name} failed: {str(e)}"
                        self.messages.append({
                            "role": "tool",
                            "content": error_msg
                        })
                        self.tracer.log_event("tool.error", agent_id=self.name,
                                            data={"tool": tool_name, "error": str(e)})
                
                # Make another call to get the final response with tool results
                logger.info(f"🔄 Making follow-up call to process tool results...")
                logger.debug(f"   Message history length: {len(self.messages)}")
                logger.debug(f"   Last message role: {self.messages[-1]['role']}")
                
                chat_params = {
                    'model': self.model,
                    'messages': self.messages,
                    'stream': self.stream,
                    'options': options if options else None,
                    'keep_alive': self.keep_alive
                }
                
                if think_param is not None:
                    chat_params['think'] = think_param
                
                logger.debug(f"   Calling model again with {len(self.messages)} messages...")
                final_response = self.client.chat(**chat_params)
                logger.info(f"✅ Received final response from model")
                logger.debug(f"   Final response content length: {len(final_response.message.content)} chars")
                logger.debug(f"   Final response content: {final_response.message.content}")
                
                # Update response to the final one for next iteration
                response = final_response
                
                # Track final response
                if hasattr(response, 'eval_count') and response.eval_count:
                    self.token_usage.add_usage(completion_tokens=response.eval_count)
                    self.stats_tracker.increment(StatType.TOKENS_OUTPUT, response.eval_count, agent_id=self.name)
            
            # Loop ends - add final message and return
            logger.info(f"✅ No more tool calls - finalizing response")

            self.add_message("assistant", response.message.content)
            self.stats_tracker.increment(StatType.CONVERSATION_TURNS, 1, agent_id=self.name)

            result = {
                "content": response.message.content,
                "tool_calls": getattr(response.message, 'tool_calls', None),
                "raw_response": response
            }
            
            # # Cache the response if caching is enabled
            # if self.enable_cache and self.cache:
            #     self.cache.set(
            #         message=message,
            #         model=self.model,
            #         response=result,
            #         options=options,
            #         tools=all_tools
            #     )
            
            return result

    async def achat(self, message: str, tools: Optional[List[Callable]] = None) -> Dict[str, Any]:
        """
        Asynchronously send a message to the agent and get a response
        """
        if self.handoff_manager:
            target_agent_id = self.handoff_manager.check_handoff_rules(message)
            if target_agent_id and target_agent_id != self.name:
                return self.handoff_manager.handoff_to(target_agent_id, context={"trigger_message": message})

        start_time = time.time()
        with self.tracer.span("agent.achat", agent_id=self.name,
                             data={"message": message, "has_tools": bool(tools)}) as span:
            self.add_message("user", message)
            all_tools = self._prepare_tools()
            if tools:
                temp_registry = ToolRegistry()
                for tool_func in tools:
                    temp_registry.register_tool(tool_func)
                all_tools.extend(temp_registry.get_ollama_tools())
            self.stats_tracker.increment(StatType.TOOLS_CALLED, len(all_tools), agent_id=self.name)
            think_param = self._get_think_param()
            options = self._get_options()
            self.stats_tracker.increment(StatType.REQUESTS_MADE, 1, agent_id=self.name)

            # Build chat parameters
            chat_params = {
                'model': self.model,
                'messages': self.messages,
                'tools': all_tools if all_tools else None,
                'stream': self.stream,
                'options': options if options else None,
                'keep_alive': self.keep_alive
            }
            
            # Only include think parameter if explicitly set
            if think_param is not None:
                chat_params['think'] = think_param
            
            response = await self.async_client.chat(**chat_params)

            response_time = time.time() - start_time
            self.stats_tracker.increment(StatType.RESPONSE_TIME, response_time, agent_id=self.name)
            if hasattr(response, 'prompt_eval_count') and response.prompt_eval_count:
                self.token_usage.add_usage(prompt_tokens=response.prompt_eval_count)
                self.stats_tracker.increment(StatType.TOKENS_INPUT, response.prompt_eval_count, agent_id=self.name)
            if hasattr(response, 'eval_count') and response.eval_count:
                self.token_usage.add_usage(completion_tokens=response.eval_count)
                self.stats_tracker.increment(StatType.TOKENS_OUTPUT, response.eval_count, agent_id=self.name)
            
            # Execute tool calls if present
            if hasattr(response.message, 'tool_calls') and response.message.tool_calls:
                self.stats_tracker.increment(StatType.TOOLS_SUCCESS, len(response.message.tool_calls), agent_id=self.name)
                
                # Add assistant's message with tool calls to history
                self.add_message("assistant", response.message.content)
                
                # Execute each tool call
                for tool_call in response.message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = tool_call.function.arguments
                    
                    self.tracer.log_event("tool.executing", agent_id=self.name, 
                                        data={"tool": tool_name, "args": tool_args})
                    
                    try:
                        # Execute the tool
                        tool_result = self.tool_registry.tools[tool_name](**tool_args)
                        
                        # Add tool result to conversation
                        self.messages.append({
                            "role": "tool",
                            "content": str(tool_result)
                        })
                        
                        self.tracer.log_event("tool.success", agent_id=self.name,
                                            data={"tool": tool_name, "result_length": len(str(tool_result))})
                    except Exception as e:
                        error_msg = f"Tool {tool_name} failed: {str(e)}"
                        self.messages.append({
                            "role": "tool",
                            "content": error_msg
                        })
                        self.tracer.log_event("tool.error", agent_id=self.name,
                                            data={"tool": tool_name, "error": str(e)})
                
                # Make another call to get the final response with tool results
                chat_params = {
                    'model': self.model,
                    'messages': self.messages,
                    'stream': self.stream,
                    'options': options if options else None,
                    'keep_alive': self.keep_alive
                }
                
                if think_param is not None:
                    chat_params['think'] = think_param
                
                final_response = await self.async_client.chat(**chat_params)
                
                # Update response to the final one
                response = final_response
                
                # Track final response
                if hasattr(response, 'eval_count') and response.eval_count:
                    self.token_usage.add_usage(completion_tokens=response.eval_count)
                    self.stats_tracker.increment(StatType.TOKENS_OUTPUT, response.eval_count, agent_id=self.name)
            
            self.add_message("assistant", response.message.content)
            self.stats_tracker.increment(StatType.CONVERSATION_TURNS, 1, agent_id=self.name)
            result = {
                "content": response.message.content,
                "tool_calls": getattr(response.message, 'tool_calls', None),
                "raw_response": response
            }
            return result
    
    def generate(self, prompt: str) -> Dict[str, Any]:
        """
        Generate content using the agent
        """
        start_time = time.time()
        with self.tracer.span("agent.generate", agent_id=self.name,
                             data={"prompt_length": len(prompt)}) as span:
            think_param = self._get_think_param()
            options = self._get_options()
            self.stats_tracker.increment(StatType.REQUESTS_MADE, 1, agent_id=self.name)
            
            # Build generate parameters
            gen_params = {
                'model': self.model,
                'prompt': prompt,
                'system': self.instructions,
                'stream': self.stream,
                'options': options if options else None,
                'keep_alive': self.keep_alive
            }
            
            # Only include think parameter if explicitly set
            if think_param is not None:
                gen_params['think'] = think_param
            
            response = self.client.generate(**gen_params)
            response_time = time.time() - start_time
            self.stats_tracker.increment(StatType.RESPONSE_TIME, response_time, agent_id=self.name)
            if hasattr(response, 'prompt_eval_count') and response.prompt_eval_count:
                self.token_usage.add_usage(prompt_tokens=response.prompt_eval_count)
                self.stats_tracker.increment(StatType.TOKENS_INPUT, response.prompt_eval_count, agent_id=self.name)
            if hasattr(response, 'eval_count') and response.eval_count:
                self.token_usage.add_usage(completion_tokens=response.eval_count)
                self.stats_tracker.increment(StatType.TOKENS_OUTPUT, response.eval_count, agent_id=self.name)
            result = {
                "content": response.response,
                "raw_response": response
            }
            return result
    
    async def agenerate(self, prompt: str) -> Dict[str, Any]:
        """
        Asynchronously generate content using the agent
        """
        with self.tracer.span("agent.agenerate", agent_id=self.name,
                             data={"prompt_length": len(prompt)}) as span:
            think_param = self._get_think_param()
            options = self._get_options()
            
            # Build generate parameters
            gen_params = {
                'model': self.model,
                'prompt': prompt,
                'system': self.instructions,
                'stream': self.stream,
                'options': options if options else None,
                'keep_alive': self.keep_alive
            }
            
            # Only include think parameter if explicitly set
            if think_param is not None:
                gen_params['think'] = think_param
            
            response = await self.async_client.generate(**gen_params)
            result = {
                "content": response.response,
                "raw_response": response
            }
            return result

    def reset_conversation(self):
        """Reset the conversation history"""
        self.messages = []
        if self.instructions:
            self.messages.append({"role": "system", "content": self.instructions})

    # Memory-related methods
    def remember(self, key: str, value: Any, expires_in: Optional[int] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Store a memory entry for this agent"""
        return self.memory_manager.set(self.name, key, value, expires_in, metadata)

    def recall(self, key: str) -> Optional[Any]:
        """Retrieve a memory entry for this agent"""
        return self.memory_manager.get(self.name, key)

    def forget(self, key: str) -> bool:
        """Delete a memory entry for this agent"""
        return self.memory_manager.delete(self.name, key)

    def get_memory_keys(self) -> List[str]:
        """List all memory keys for this agent"""
        return self.memory_manager.list_keys(self.name)

    def clear_memory(self) -> bool:
        """Clear all memory for this agent"""
        return self.memory_manager.clear_agent_memory(self.name)

    def get_memory_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a memory entry"""
        return self.memory_manager.get_metadata(self.name, key)

    def cleanup_expired_memory(self) -> int:
        """Clean up expired memory entries"""
        return self.memory_manager.cleanup_expired()

    def get_tracer(self):
        """Get the tracer instance for this agent"""
        return self.tracer

    def get_trace_store(self):
        """Get the trace store for this agent"""
        return self.tracer.get_trace_store()

    def export_trace_session(self, session_id: Optional[str] = None) -> str:
        """Export the trace session to JSON"""
        return self.tracer.export_session(session_id)

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        pass

    def __enter__(self):
        """Sync context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context manager exit"""
        pass