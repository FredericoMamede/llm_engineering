"""
Rate limiting: per-user/session rate limits with token bucket algorithm.

Features:
- Per-session rate limiting
- Token bucket algorithm
- Configurable limits (requests per minute, tokens per hour)
- Cost-based rate limiting
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Optional

from core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RateLimit:
    """Rate limit configuration for a session."""
    requests_per_minute: int = 60
    tokens_per_hour: int = 100000
    cost_per_hour: float = 10.0  # USD
    
    # Token bucket state
    request_tokens: float = field(default_factory=lambda: 60.0)  # Start with full bucket
    token_tokens: float = field(default_factory=lambda: 100000.0)
    cost_tokens: float = field(default_factory=lambda: 10.0)
    
    # Timestamps
    last_request_time: float = field(default_factory=time.time)
    last_token_time: float = field(default_factory=time.time)
    last_cost_time: float = field(default_factory=time.time)


class RateLimiter:
    """
    Rate limiter using token bucket algorithm.
    
    Tracks limits per session_id:
    - Requests per minute
    - Tokens per hour
    - Cost per hour (USD)
    """
    
    def __init__(
        self,
        default_requests_per_minute: int = 60,
        default_tokens_per_hour: int = 100000,
        default_cost_per_hour: float = 10.0,
    ) -> None:
        """
        Initialize rate limiter.
        
        Args:
            default_requests_per_minute: Default request limit per minute
            default_tokens_per_hour: Default token limit per hour
            default_cost_per_hour: Default cost limit per hour (USD)
        """
        self.default_limits = RateLimit(
            requests_per_minute=default_requests_per_minute,
            tokens_per_hour=default_tokens_per_hour,
            cost_per_hour=default_cost_per_hour,
        )
        self.limits: Dict[str, RateLimit] = defaultdict(lambda: self.default_limits)
    
    def _refill_tokens(self, limit: RateLimit, current_time: float) -> None:
        """Refill token buckets based on elapsed time."""
        # Refill request tokens (per minute)
        elapsed_minutes = (current_time - limit.last_request_time) / 60.0
        if elapsed_minutes > 0:
            tokens_to_add = elapsed_minutes * limit.requests_per_minute
            limit.request_tokens = min(limit.requests_per_minute, limit.request_tokens + tokens_to_add)
            limit.last_request_time = current_time
        
        # Refill token tokens (per hour)
        elapsed_hours = (current_time - limit.last_token_time) / 3600.0
        if elapsed_hours > 0:
            tokens_to_add = elapsed_hours * limit.tokens_per_hour
            limit.token_tokens = min(limit.tokens_per_hour, limit.token_tokens + tokens_to_add)
            limit.last_token_time = current_time
        
        # Refill cost tokens (per hour)
        elapsed_hours = (current_time - limit.last_cost_time) / 3600.0
        if elapsed_hours > 0:
            tokens_to_add = elapsed_hours * limit.cost_per_hour
            limit.cost_tokens = min(limit.cost_per_hour, limit.cost_tokens + tokens_to_add)
            limit.last_cost_time = current_time
    
    def check_request(self, session_id: str) -> tuple[bool, Optional[str]]:
        """
        Check if a request is allowed.
        
        Args:
            session_id: Session identifier
        
        Returns:
            (allowed, error_message)
        """
        current_time = time.time()
        limit = self.limits[session_id]
        
        # Refill tokens
        self._refill_tokens(limit, current_time)
        
        # Check request limit
        if limit.request_tokens < 1.0:
            wait_time = 60.0 / limit.requests_per_minute
            logger.warning(
                f"Rate limit exceeded: requests per minute for session {session_id[:8]}",
                extra={"session_id": session_id, "limit_type": "requests_per_minute", "wait_time": wait_time},
            )
            return False, f"Rate limit exceeded. Please wait {wait_time:.1f} seconds before making another request."
        
        # Consume request token
        limit.request_tokens -= 1.0
        limit.last_request_time = current_time
        
        return True, None
    
    def check_tokens(self, session_id: str, token_count: int) -> tuple[bool, Optional[str]]:
        """
        Check if token usage is allowed.
        
        Args:
            session_id: Session identifier
            token_count: Number of tokens to use
        
        Returns:
            (allowed, error_message)
        """
        current_time = time.time()
        limit = self.limits[session_id]
        
        # Refill tokens
        self._refill_tokens(limit, current_time)
        
        # Check token limit
        if limit.token_tokens < token_count:
            remaining = limit.token_tokens
            logger.warning(
                f"Rate limit exceeded: tokens per hour for session {session_id[:8]}",
                extra={
                    "session_id": session_id,
                    "limit_type": "tokens_per_hour",
                    "requested": token_count,
                    "remaining": remaining,
                },
            )
            return False, f"Token limit exceeded. You have {remaining:.0f} tokens remaining this hour."
        
        # Consume tokens
        limit.token_tokens -= token_count
        limit.last_token_time = current_time
        
        return True, None
    
    def check_cost(self, session_id: str, cost: float) -> tuple[bool, Optional[str]]:
        """
        Check if cost is allowed.
        
        Args:
            session_id: Session identifier
            cost: Cost in USD
        
        Returns:
            (allowed, error_message)
        """
        current_time = time.time()
        limit = self.limits[session_id]
        
        # Refill tokens
        self._refill_tokens(limit, current_time)
        
        # Check cost limit
        if limit.cost_tokens < cost:
            remaining = limit.cost_tokens
            logger.warning(
                f"Rate limit exceeded: cost per hour for session {session_id[:8]}",
                extra={
                    "session_id": session_id,
                    "limit_type": "cost_per_hour",
                    "requested": cost,
                    "remaining": remaining,
                },
            )
            return False, f"Cost limit exceeded. You have ${remaining:.2f} remaining this hour."
        
        # Consume cost
        limit.cost_tokens -= cost
        limit.last_cost_time = current_time
        
        return True, None
    
    def record_usage(self, session_id: str, tokens: int = 0, cost: float = 0.0) -> None:
        """
        Record token and cost usage (after successful request).
        
        Args:
            session_id: Session identifier
            tokens: Number of tokens used
            cost: Cost in USD
        """
        if tokens > 0:
            self.check_tokens(session_id, tokens)  # This will consume tokens
        if cost > 0:
            self.check_cost(session_id, cost)  # This will consume cost
    
    def get_remaining(self, session_id: str) -> Dict[str, float]:
        """
        Get remaining limits for a session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Dict with remaining requests, tokens, and cost
        """
        current_time = time.time()
        limit = self.limits[session_id]
        self._refill_tokens(limit, current_time)
        
        return {
            "requests_remaining": limit.request_tokens,
            "tokens_remaining": limit.token_tokens,
            "cost_remaining": limit.cost_tokens,
        }
    
    def reset_session(self, session_id: str) -> None:
        """Reset rate limits for a session."""
        if session_id in self.limits:
            del self.limits[session_id]
            logger.info(f"Reset rate limits for session {session_id[:8]}")


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get or create global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        import os
        requests_per_min = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MIN", "60"))
        tokens_per_hour = int(os.getenv("RATE_LIMIT_TOKENS_PER_HOUR", "100000"))
        cost_per_hour = float(os.getenv("RATE_LIMIT_COST_PER_HOUR", "10.0"))
        _rate_limiter = RateLimiter(requests_per_min, tokens_per_hour, cost_per_hour)
    return _rate_limiter

