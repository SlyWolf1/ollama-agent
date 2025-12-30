"""
Context management with truncation options for Ollama Agents SDK
"""
from typing import List, Dict, Any, Optional
from enum import Enum
import ollama


class TruncationStrategy(Enum):
    """Different strategies for context truncation"""
    OLDEST_FIRST = "oldest_first"
    NEWEST_FIRST = "newest_first"
    SUMMARIZE_MIDDLE = "summarize_middle"
    CUSTOM = "custom"


class ContextManager:
    """Manages conversation context with various truncation strategies"""
    
    def __init__(self, max_context_length: int = 20000, strategy: TruncationStrategy = TruncationStrategy.OLDEST_FIRST):
        self.max_context_length = max_context_length
        self.strategy = strategy
        self.messages: List[Dict[str, Any]] = []
        self.original_system_prompt: Optional[str] = None
    
    def add_message(self, role: str, content: str):
        """Add a message to the context"""
        message = {"role": role, "content": content}
        self.messages.append(message)
        
        # Store the original system prompt separately to preserve it
        if role == "system" and len(self.messages) == 1:
            self.original_system_prompt = content
    
    def get_context_length(self) -> int:
        """Get the current context length in characters"""
        return sum(len(msg.get("content", "")) for msg in self.messages)
    
    def needs_truncation(self) -> bool:
        """Check if the context needs to be truncated"""
        return self.get_context_length() > self.max_context_length
    
    def truncate_context(self, client: ollama.Client, model: str) -> List[Dict[str, Any]]:
        """Truncate the context based on the selected strategy"""
        if not self.needs_truncation():
            return self.messages[:]
        
        if self.strategy == TruncationStrategy.OLDEST_FIRST:
            return self._truncate_oldest_first()
        elif self.strategy == TruncationStrategy.NEWEST_FIRST:
            return self._truncate_newest_first()
        elif self.strategy == TruncationStrategy.SUMMARIZE_MIDDLE:
            return self._truncate_with_summarization(client, model)
        else:  # CUSTOM or fallback
            return self._truncate_oldest_first()  # Default to oldest first
    
    def _truncate_oldest_first(self) -> List[Dict[str, Any]]:
        """Remove oldest messages first until context is within limits"""
        if not self.needs_truncation():
            return self.messages[:]
        
        # Keep the system prompt if it exists
        system_messages = [msg for msg in self.messages if msg["role"] == "system"]
        non_system_messages = [msg for msg in self.messages if msg["role"] != "system"]
        
        # Start with system messages
        truncated_messages = system_messages[:]
        
        # Add messages from the end (newest) until we reach the limit
        current_length = sum(len(msg.get("content", "")) for msg in truncated_messages)
        
        for msg in reversed(non_system_messages):
            msg_length = len(msg.get("content", ""))
            if current_length + msg_length <= self.max_context_length:
                truncated_messages.insert(len(system_messages), msg)
                current_length += msg_length
            else:
                break
        
        # Reverse the order to maintain chronological sequence
        result = truncated_messages[:len(system_messages)]  # System messages first
        result.extend(reversed(truncated_messages[len(system_messages):]))
        
        return result
    
    def _truncate_newest_first(self) -> List[Dict[str, Any]]:
        """Remove newest messages first until context is within limits"""
        if not self.needs_truncation():
            return self.messages[:]
        
        # Keep the system prompt if it exists
        system_messages = [msg for msg in self.messages if msg["role"] == "system"]
        non_system_messages = [msg for msg in self.messages if msg["role"] != "system"]
        
        # Start with system messages
        truncated_messages = system_messages[:]
        current_length = sum(len(msg.get("content", "")) for msg in system_messages)
        
        # Add messages from the beginning (oldest) until we reach the limit
        for msg in non_system_messages:
            msg_length = len(msg.get("content", ""))
            if current_length + msg_length <= self.max_context_length:
                truncated_messages.append(msg)
                current_length += msg_length
            else:
                break
        
        return truncated_messages
    
    def _truncate_with_summarization(self, client: ollama.Client, model: str) -> List[Dict[str, Any]]:
        """Summarize the middle portion of the conversation to reduce context"""
        if not self.needs_truncation():
            return self.messages[:]
        
        # Keep system messages and the most recent messages
        system_messages = [msg for msg in self.messages if msg["role"] == "system"]
        non_system_messages = [msg for msg in self.messages if msg["role"] != "system"]
        
        if len(non_system_messages) <= 2:  # Not enough messages to summarize
            return self.messages[:self.max_context_length//100]  # Just truncate to first few messages
        
        # Keep first and last few messages, summarize the middle
        keep_from_start = max(1, len(non_system_messages) // 4)  # Keep 25% from start
        keep_from_end = max(1, len(non_system_messages) // 4)    # Keep 25% from end
        
        start_messages = non_system_messages[:keep_from_start]
        middle_messages = non_system_messages[keep_from_start:-keep_from_end if keep_from_end > 0 else len(non_system_messages)]
        end_messages = non_system_messages[-keep_from_end:]
        
        # Summarize the middle portion
        if middle_messages:
            middle_text = " ".join([f"{msg['role']}: {msg['content']}" for msg in middle_messages])
            
            try:
                # Use the model to generate a summary of the middle portion
                summary_prompt = f"Please provide a concise summary of the following conversation segment:\n\n{middle_text}\n\nSummary:"
                summary_response = client.generate(
                    model=model,
                    prompt=summary_prompt,
                    options={"num_predict": 200, "temperature": 0.3}
                )
                
                # Create a summary message
                summary_msg = {
                    "role": "system",
                    "content": f"Summary of previous conversation: {summary_response.response}"
                }
            except Exception:
                # If summarization fails, just truncate the middle
                summary_msg = {
                    "role": "system",
                    "content": "Previous conversation (truncated)"
                }
        else:
            summary_msg = None
        
        # Combine all parts
        result = system_messages[:]
        result.extend(start_messages)
        
        if summary_msg:
            result.append(summary_msg)
        
        result.extend(end_messages)
        
        # If still too long, apply simple truncation
        if sum(len(msg.get("content", "")) for msg in result) > self.max_context_length:
            # Fall back to oldest-first truncation
            temp_manager = ContextManager(self.max_context_length, TruncationStrategy.OLDEST_FIRST)
            for msg in result:
                temp_manager.add_message(msg["role"], msg["content"])
            return temp_manager.truncate_context(client, model)
        
        return result
    
    def get_truncated_messages(self, client: ollama.Client, model: str) -> List[Dict[str, Any]]:
        """Get messages with truncation applied if needed"""
        if self.needs_truncation():
            return self.truncate_context(client, model)
        return self.messages[:]


# Update the Agent class to use the ContextManager
def apply_context_management(agent, messages: List[Dict[str, Any]], client: ollama.Client, model: str) -> List[Dict[str, Any]]:
    """
    Apply context management to a list of messages
    """
    context_manager = ContextManager(
        max_context_length=agent.max_context_length,
        strategy=TruncationStrategy.SUMMARIZE_MIDDLE  # Default strategy
    )
    
    for msg in messages:
        context_manager.add_message(msg["role"], msg["content"])
    
    return context_manager.get_truncated_messages(client, model)