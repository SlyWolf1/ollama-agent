"""
Agent handoff functionality for transferring conversations between agents
"""
import time
from typing import Dict, Any, Optional, List, Callable
from .agent import Agent
from .stats import get_stats_tracker, StatType, TokenUsage
from .tracing import get_tracer, TraceLevel, PerformanceMetrics
from .logger import get_logger


class AgentHandoff:
    """Handles transferring conversations between different agents"""

    def __init__(self, agents: Dict[str, Agent]):
        self.agents = agents
        self.current_agent_id: Optional[str] = None
        self.handoff_rules: List[Dict[str, Any]] = []

        # Initialize tracing
        self.tracer = get_tracer()

        # Initialize stats tracking
        self.stats_tracker = get_stats_tracker()

        # Initialize logging
        self.logger = get_logger()

    def set_current_agent(self, agent_id: str):
        """Set the current active agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent '{agent_id}' not found in registry")
        self.current_agent_id = agent_id

    def get_current_agent(self) -> Optional[Agent]:
        """Get the current active agent"""
        if self.current_agent_id is None:
            return None
        return self.agents.get(self.current_agent_id)

    def add_handoff_rule(self, condition: Callable[[str], bool], target_agent_id: str, priority: int = 0):
        """
        Add a rule for automatic handoffs based on message content

        Args:
            condition: A function that takes a message and returns True if handoff should occur
            target_agent_id: ID of the target agent for this rule
            priority: Priority of the rule (higher number = higher priority)
        """
        self.handoff_rules.append({
            "condition": condition,
            "target_agent_id": target_agent_id,
            "priority": priority
        })
        # Sort rules by priority (highest first)
        self.handoff_rules.sort(key=lambda x: x["priority"], reverse=True)

    def check_handoff_rules(self, message: str) -> Optional[str]:
        """
        Check if any handoff rules match the message

        Args:
            message: The message to check against rules

        Returns:
            Target agent ID if a rule matches, None otherwise
        """
        for rule in self.handoff_rules:
            if rule["condition"](message):
                return rule["target_agent_id"]
        return None

    def handoff_to(self, target_agent_id: str, context: Optional[Dict[str, Any]] = None,
                   transfer_history: bool = True,
                   use_context_summarization: bool = True,
                   max_context_length: Optional[int] = None) -> Dict[str, Any]:
        """
        Handoff the conversation to another agent

        Args:
            target_agent_id: ID of the target agent to handoff to
            context: Optional context to pass to the target agent
            transfer_history: Whether to transfer conversation history to the target agent
            use_context_summarization: Whether to summarize context if it's too long
            max_context_length: Maximum context length before summarization is triggered

        Returns:
            Response from the target agent
        """
        start_time = time.time()

        # Prepare token usage for tracing
        token_usage = TokenUsage()
        performance = PerformanceMetrics()

        with self.tracer.span("handoff.execute",
                             data={"target_agent_id": target_agent_id,
                                   "has_context": context is not None,
                                   "transfer_history": transfer_history,
                                   "use_context_summarization": use_context_summarization},
                             token_usage=token_usage,
                             performance=performance) as span:
            if target_agent_id not in self.agents:
                raise ValueError(f"Target agent '{target_agent_id}' not found in registry")

            target_agent = self.agents[target_agent_id]

            # Get the current agent's messages to pass as context
            current_agent = self.get_current_agent()
            if current_agent and transfer_history:
                # Check if context summarization is needed
                if use_context_summarization and current_agent.should_summarize_context():
                    # Summarize the context before transferring
                    summary_start = time.time()
                    summary_message = current_agent.get_context_summary_message()
                    summary_time = time.time() - summary_start

                    target_agent.add_message("system", summary_message["content"])

                    # Log the summarization timing
                    self.tracer.log_event(
                        "context.summarization",
                        data={
                            "summary_time": summary_time,
                            "summary_length": len(summary_message["content"])
                        }
                    )

                    # Log the summarization
                    self.logger.info(
                        f"Context summarized during handoff from {current_agent.model} to {target_agent.model}",
                        extra={"summary_length": len(summary_message["content"]),
                               "summary_time": f"{summary_time:.3f}s"}
                    )
                else:
                    # Transfer the conversation history to the target agent
                    transfer_start = time.time()
                    if context:
                        # Add context as a system message
                        target_agent.add_message("system", f"Context from previous agent: {context}")

                    # Copy the conversation history (excluding system messages to avoid duplication)
                    for message in current_agent.messages:
                        if message["role"] != "system" or message.get("content") != current_agent.instructions:
                            target_agent.messages.append(message)

                    transfer_time = time.time() - transfer_start

                    # Log the transfer timing
                    self.tracer.log_event(
                        "context.transfer",
                        data={
                            "transfer_time": transfer_time,
                            "messages_transferred": len(current_agent.messages)
                        }
                    )
            elif context:
                # If no current agent or not transferring history, at least pass the context
                target_agent.add_message("system", f"Handoff context: {context}")

            # Set the target agent as current
            previous_agent_id = self.current_agent_id
            self.current_agent_id = target_agent_id

            # Calculate response time
            response_time = time.time() - start_time

            # Track agent switch
            self.stats_tracker.increment(StatType.AGENT_SWITCHES, 1)

            # Track response time
            self.stats_tracker.increment(StatType.RESPONSE_TIME, response_time)

            # Calculate performance metrics
            performance.response_time = response_time
            if response_time > 0:
                performance.tokens_per_second = 0  # No tokens processed in handoff, but we track time
                performance.processing_time = response_time

            # Update span with performance metrics
            if span:
                span.performance = performance

            # Log the handoff with Rich visuals
            self.logger.log_handoff(
                from_agent=previous_agent_id or "None",
                to_agent=target_agent_id,
                reason=f"Context length: {len(current_agent.messages) if current_agent else 0} messages"
            )

            # Log the handoff if tracing is enabled
            if self.tracer.level in [TraceLevel.STANDARD, TraceLevel.VERBOSE]:
                self.tracer.log_event("handoff.completed",
                                     data={"from_agent": previous_agent_id,
                                           "to_agent": target_agent_id,
                                           "context_provided": context is not None,
                                           "response_time": response_time,
                                           "context_summarized": use_context_summarization and current_agent and current_agent.should_summarize_context()})

            # Return the target agent for further interaction
            result = {
                "target_agent": target_agent,
                "message": f"Handoff completed to agent '{target_agent_id}'",
                "previous_agent_id": previous_agent_id
            }

            # Add result to span data
            if span is not None:
                span.data.update({"handoff_successful": True,
                                 "from_agent": previous_agent_id,
                                 "to_agent": target_agent_id,
                                 "response_time": response_time})

            return result

    def chat_with_current(self, message: str) -> Dict[str, Any]:
        """Send a message to the current agent, checking for automatic handoffs"""
        start_time = time.time()

        with self.tracer.span("handoff.chat_with_current",
                             data={"message_length": len(message),
                                   "current_agent_id": self.current_agent_id}) as span:
            # Check if any handoff rules apply to this message
            target_agent_id = self.check_handoff_rules(message)
            if target_agent_id:
                result = self.handoff_to(target_agent_id, context={"trigger_message": message})

                # Log the automatic handoff
                if self.tracer.level in [TraceLevel.STANDARD, TraceLevel.VERBOSE]:
                    self.tracer.log_event("handoff.automatic_triggered",
                                         data={"trigger_message": message,
                                               "target_agent_id": target_agent_id})

                # Track agent switch
                self.stats_tracker.increment(StatType.AGENT_SWITCHES, 1)

                return result

            current_agent = self.get_current_agent()
            if not current_agent:
                raise ValueError("No current agent set. Use set_current_agent() first.")

            response = current_agent.chat(message)

            # Calculate response time
            response_time = time.time() - start_time

            # Track response time
            self.stats_tracker.increment(StatType.RESPONSE_TIME, response_time)

            # Add response info to span data
            if span is not None:
                span.data.update({"response_length": len(response.get("content", "")),
                                 "has_tool_calls": bool(response.get("tool_calls")),
                                 "response_time": response_time})

            return response

    async def achat_with_current(self, message: str) -> Dict[str, Any]:
        """Asynchronously send a message to the current agent, checking for automatic handoffs"""
        start_time = time.time()

        with self.tracer.span("handoff.achat_with_current",
                             data={"message_length": len(message),
                                   "current_agent_id": self.current_agent_id}) as span:
            # Check if any handoff rules apply to this message
            target_agent_id = self.check_handoff_rules(message)
            if target_agent_id:
                result = self.handoff_to(target_agent_id, context={"trigger_message": message})

                # Log the automatic handoff
                if self.tracer.level in [TraceLevel.STANDARD, TraceLevel.VERBOSE]:
                    self.tracer.log_event("handoff.automatic_triggered",
                                         data={"trigger_message": message,
                                               "target_agent_id": target_agent_id})

                # Track agent switch
                self.stats_tracker.increment(StatType.AGENT_SWITCHES, 1)

                return result

            current_agent = self.get_current_agent()
            if not current_agent:
                raise ValueError("No current agent set. Use set_current_agent() first.")

            response = await current_agent.achat(message)

            # Calculate response time
            response_time = time.time() - start_time

            # Track response time
            self.stats_tracker.increment(StatType.RESPONSE_TIME, response_time)

            # Add response info to span data
            if span is not None:
                span.data.update({"response_length": len(response.get("content", "")),
                                 "has_tool_calls": bool(response.get("tool_calls")),
                                 "response_time": response_time})

            return response

    def add_agent(self, agent_id: str, agent: Agent):
        """Add an agent to the handoff registry"""
        self.agents[agent_id] = agent

    def get_tracer(self):
        """Get the tracer instance for this handoff manager"""
        return self.tracer

    def get_trace_store(self):
        """Get the trace store for this handoff manager"""
        return self.tracer.get_trace_store()

    def export_trace_session(self, session_id: Optional[str] = None) -> str:
        """Export the trace session to JSON"""
        return self.tracer.export_session(session_id)

    def get_stats(self) -> Dict[StatType, float]:
        """Get current statistics for this handoff manager"""
        return {stat_type: self.stats_tracker.get(stat_type)
                for stat_type in StatType}

    def export_stats(self, session_id: Optional[str] = None) -> str:
        """Export statistics to JSON format"""
        return self.stats_tracker.export_stats(session_id)

    def export_stat_records(self) -> str:
        """Export all stat records to JSON format"""
        return self.stats_tracker.export_records()