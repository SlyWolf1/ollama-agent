"""
Retry functionality for Ollama Agents SDK
Provides automatic retry with exponential backoff for API calls
"""
import time
import functools
from typing import Callable, Optional, Type, Tuple, Any
from dataclasses import dataclass
import ollama


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retry_on_exceptions: Tuple[Type[Exception], ...] = (
        ollama.ResponseError,
        ConnectionError,
        TimeoutError,
    )


class RetryExhausted(Exception):
    """Raised when all retry attempts are exhausted"""
    pass


def calculate_backoff(
    attempt: int,
    initial_delay: float,
    exponential_base: float,
    max_delay: float,
    jitter: bool = True
) -> float:
    """
    Calculate backoff delay with exponential backoff and optional jitter
    
    Args:
        attempt: Current attempt number (0-indexed)
        initial_delay: Initial delay in seconds
        exponential_base: Base for exponential calculation
        max_delay: Maximum delay cap
        jitter: Whether to add random jitter
        
    Returns:
        Delay in seconds
    """
    import random
    
    # Exponential backoff: initial_delay * (base ^ attempt)
    delay = min(initial_delay * (exponential_base ** attempt), max_delay)
    
    # Add jitter: random value between 0 and delay
    if jitter:
        delay = random.uniform(0, delay)
    
    return delay


def with_retry(
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    Decorator to add retry logic to a function
    
    Args:
        config: Retry configuration (uses default if None)
        on_retry: Callback function called on each retry attempt
        
    Example:
        @with_retry(RetryConfig(max_retries=5))
        def my_api_call():
            return client.chat(...)
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                
                except config.retry_on_exceptions as e:
                    last_exception = e
                    
                    if attempt >= config.max_retries:
                        # All retries exhausted
                        raise RetryExhausted(
                            f"Failed after {config.max_retries} retries: {str(e)}"
                        ) from e
                    
                    # Calculate backoff delay
                    delay = calculate_backoff(
                        attempt,
                        config.initial_delay,
                        config.exponential_base,
                        config.max_delay,
                        config.jitter
                    )
                    
                    # Call retry callback if provided
                    if on_retry:
                        on_retry(e, attempt + 1)
                    
                    # Wait before retrying
                    time.sleep(delay)
                
                except Exception as e:
                    # Non-retryable exception, raise immediately
                    raise
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
        
        return wrapper
    
    return decorator


async def async_with_retry(
    func: Callable,
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None,
    *args,
    **kwargs
) -> Any:
    """
    Async version of retry logic
    
    Args:
        func: Async function to call
        config: Retry configuration
        on_retry: Callback on retry
        *args, **kwargs: Arguments to pass to func
        
    Returns:
        Result of func call
    """
    import asyncio
    
    if config is None:
        config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(config.max_retries + 1):
        try:
            return await func(*args, **kwargs)
        
        except config.retry_on_exceptions as e:
            last_exception = e
            
            if attempt >= config.max_retries:
                raise RetryExhausted(
                    f"Failed after {config.max_retries} retries: {str(e)}"
                ) from e
            
            delay = calculate_backoff(
                attempt,
                config.initial_delay,
                config.exponential_base,
                config.max_delay,
                config.jitter
            )
            
            if on_retry:
                on_retry(e, attempt + 1)
            
            await asyncio.sleep(delay)
        
        except Exception as e:
            raise
    
    if last_exception:
        raise last_exception


# Global retry configuration
_global_retry_config: Optional[RetryConfig] = None


def get_retry_config() -> Optional[RetryConfig]:
    """Get the global retry configuration"""
    return _global_retry_config


def set_global_retry_config(config: RetryConfig):
    """Set global retry configuration"""
    global _global_retry_config
    _global_retry_config = config


def disable_retry():
    """Disable global retry"""
    global _global_retry_config
    _global_retry_config = None
