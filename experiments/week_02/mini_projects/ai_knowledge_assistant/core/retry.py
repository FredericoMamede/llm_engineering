"""
Retry logic with exponential backoff for API calls.

Features:
- Exponential backoff with jitter
- Configurable max retries
- Retry on specific error types
- Context-aware retry decisions
"""

import random
import time
from functools import wraps
from typing import Any, Callable, Optional

from core.logger import get_logger

logger = get_logger(__name__)


def should_retry(error: Exception) -> bool:
    """
    Determine if an error should trigger a retry.
    
    Args:
        error: The exception that occurred
    
    Returns:
        True if error is retryable, False otherwise
    """
    from openai import AuthenticationError, APIConnectionError, RateLimitError
    
    # Never retry authentication errors
    if isinstance(error, AuthenticationError):
        return False
    
    # Always retry connection errors (transient)
    if isinstance(error, APIConnectionError):
        return True
    
    # Retry rate limits (with backoff)
    if isinstance(error, RateLimitError):
        return True
    
    # Check error string for retryable patterns
    error_str = str(error).lower()
    
    # Retry on transient errors
    retryable_patterns = [
        "timeout",
        "connection",
        "network",
        "503",  # Service unavailable
        "502",  # Bad gateway
        "504",  # Gateway timeout
        "429",  # Rate limit
    ]
    
    if any(pattern in error_str for pattern in retryable_patterns):
        return True
    
    # Don't retry on client errors (4xx except 429)
    if "400" in error_str or "401" in error_str or "403" in error_str or "404" in error_str:
        return False
    
    # Default: retry on unknown errors (might be transient)
    return True


def exponential_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0, jitter: bool = True) -> float:
    """
    Calculate exponential backoff delay.
    
    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        jitter: Add random jitter to prevent thundering herd
    
    Returns:
        Delay in seconds
    """
    delay = min(base_delay * (2 ** attempt), max_delay)
    
    if jitter:
        # Add ±25% jitter
        jitter_amount = delay * 0.25
        delay = delay + random.uniform(-jitter_amount, jitter_amount)
        delay = max(0.1, delay)  # Minimum 100ms
    
    return delay


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    on_retry: Optional[Callable[[int, Exception], None]] = None,
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff
        max_delay: Maximum delay in seconds
        on_retry: Optional callback called before each retry (attempt_num, error)
    
    Example:
        @retry_with_backoff(max_retries=3)
        def api_call():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_error = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                
                except Exception as e:
                    last_error = e
                    
                    # Check if error is retryable
                    if not should_retry(e):
                        logger.debug(
                            f"Non-retryable error in {func.__name__}: {e}",
                            extra={"function": func.__name__, "error_type": type(e).__name__},
                        )
                        raise
                    
                    # Check if we've exhausted retries
                    if attempt >= max_retries:
                        logger.warning(
                            f"Max retries ({max_retries}) exceeded for {func.__name__}",
                            extra={
                                "function": func.__name__,
                                "attempts": attempt + 1,
                                "error": str(e)[:200],
                            },
                        )
                        raise
                    
                    # Calculate backoff delay
                    delay = exponential_backoff(attempt, base_delay, max_delay)
                    
                    # Call retry callback if provided
                    if on_retry:
                        on_retry(attempt + 1, e)
                    
                    logger.info(
                        f"Retrying {func.__name__} (attempt {attempt + 1}/{max_retries}) after {delay:.2f}s",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt + 1,
                            "max_retries": max_retries,
                            "delay": delay,
                            "error": str(e)[:200],
                        },
                    )
                    
                    time.sleep(delay)
            
            # Should never reach here, but just in case
            if last_error:
                raise last_error
            raise RuntimeError(f"Unexpected retry loop exit in {func.__name__}")
        
        return wrapper
    return decorator


def retry_api_call(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    **kwargs
) -> Any:
    """
    Retry an API call with exponential backoff.
    
    Convenience function for one-off retries.
    
    Args:
        func: Function to call
        max_retries: Maximum retry attempts
        base_delay: Base delay for backoff
        **kwargs: Arguments to pass to func
    
    Returns:
        Result from func
    
    Raises:
        Last exception if all retries fail
    """
    @retry_with_backoff(max_retries=max_retries, base_delay=base_delay)
    def _call():
        return func(**kwargs)
    
    return _call()

