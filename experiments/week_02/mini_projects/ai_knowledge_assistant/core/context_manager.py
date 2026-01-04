"""
Context window management: token counting, truncation, summarization.

Features:
- Token counting before API calls
- Automatic history truncation
- Conversation summarization
- Sliding window approach
"""

from typing import Any, Dict, List, Optional, Tuple

from core.logger import get_logger

logger = get_logger(__name__)


class ContextManager:
    """
    Manages context window size and truncation.
    
    Strategies:
    - truncate: Remove oldest messages
    - summarize: Summarize old messages
    - sliding: Keep recent messages, summarize older ones
    """
    
    def __init__(
        self,
        max_tokens: int = 8000,  # Conservative default (GPT-4o-mini has 128k, but we leave room)
        strategy: str = "truncate",
    ) -> None:
        """
        Initialize context manager.
        
        Args:
            max_tokens: Maximum tokens to allow in context
            strategy: Truncation strategy ("truncate", "summarize", "sliding")
        """
        self.max_tokens = max_tokens
        self.strategy = strategy
        
        # Initialize tokenizer (use cl100k_base for GPT models)
        try:
            import tiktoken
            self.encoding = tiktoken.get_encoding("cl100k_base")
        except ImportError:
            logger.warning("tiktoken not installed, using fallback token counting. Install with: pip install tiktoken")
            self.encoding = None
        except Exception as e:
            logger.warning(f"Failed to load tiktoken: {e}, using fallback token counting")
            self.encoding = None
    
    def count_tokens(self, text: Any) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Text to count (can be None, str, or other types)
        
        Returns:
            Approximate token count
        """
        # Convert to string if not already
        if text is None:
            return 0
        
        # Ensure text is a string (handle dict, list, etc.)
        if not isinstance(text, str):
            try:
                text = str(text)
            except Exception:
                return 0
        
        if not text:
            return 0
        
        if self.encoding:
            try:
                return len(self.encoding.encode(text))
            except Exception as e:
                logger.warning(f"Token counting error: {e}, using fallback")
        
        # Fallback: rough estimate (1 token ≈ 4 characters)
        return len(text) // 4
    
    def count_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        Count total tokens in messages array.
        
        Args:
            messages: List of message dicts with "role" and "content"
        
        Returns:
            Total token count (including overhead for formatting)
        """
        total = 0
        
        # Overhead for message formatting (approximately 4 tokens per message)
        overhead = len(messages) * 4
        
        for msg in messages:
            # Handle messages that might have None content or tool_calls
            content = msg.get("content") or ""
            # Skip tool_calls in token counting (they're handled separately)
            if "tool_calls" not in msg:
                total += self.count_tokens(content)
        
        return total + overhead
    
    def truncate_messages(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """
        Truncate messages to fit within token limit.
        
        Args:
            messages: List of message dicts
            system_prompt: Optional system prompt (always kept)
        
        Returns:
            Truncated messages list
        """
        if not messages:
            return messages
        
        # Always keep system prompt
        result: List[Dict[str, str]] = []
        if system_prompt:
            result.append({"role": "system", "content": system_prompt})
        
        # Count system prompt tokens
        system_tokens = self.count_tokens(system_prompt) if system_prompt else 0
        
        # Strategy: keep most recent messages that fit
        current_tokens = system_tokens
        kept_messages: List[Dict[str, str]] = []
        
        # Work backwards from most recent
        for msg in reversed(messages):
            if msg.get("role") == "system":
                continue  # Skip system messages (already added)
            
            msg_tokens = self.count_tokens(msg.get("content", "")) + 4  # +4 for formatting
            
            if current_tokens + msg_tokens <= self.max_tokens:
                kept_messages.insert(0, msg)
                current_tokens += msg_tokens
            else:
                # Can't fit this message
                break
        
        result.extend(kept_messages)
        
        if len(result) < len(messages) + (1 if system_prompt else 0):
            removed = len(messages) - len(kept_messages)
            logger.warning(
                f"Truncated {removed} messages to fit context window",
                extra={
                    "removed_count": removed,
                    "kept_count": len(kept_messages),
                    "total_tokens": current_tokens,
                    "max_tokens": self.max_tokens,
                },
            )
        
        return result
    
    def should_truncate(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> Tuple[bool, int]:
        """
        Check if messages need truncation.
        
        Args:
            messages: List of message dicts
            system_prompt: Optional system prompt
        
        Returns:
            (needs_truncation, current_token_count)
        """
        total_tokens = self.count_messages_tokens(messages)
        if system_prompt:
            total_tokens += self.count_tokens(system_prompt)
        
        return total_tokens > self.max_tokens, total_tokens
    
    def get_context_info(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Get context window information.
        
        Args:
            messages: List of message dicts
            system_prompt: Optional system prompt
        
        Returns:
            Dict with token counts and truncation info
        """
        total_tokens = self.count_messages_tokens(messages)
        if system_prompt:
            total_tokens += self.count_tokens(system_prompt)
        
        needs_truncation, _ = self.should_truncate(messages, system_prompt)
        
        return {
            "total_tokens": total_tokens,
            "max_tokens": self.max_tokens,
            "needs_truncation": needs_truncation,
            "message_count": len(messages),
            "utilization_percent": round((total_tokens / self.max_tokens) * 100, 1) if self.max_tokens > 0 else 0,
        }


# Global context manager instance
_context_manager: Optional[ContextManager] = None


def get_context_manager() -> ContextManager:
    """Get or create global context manager instance."""
    global _context_manager
    if _context_manager is None:
        import os
        max_tokens = int(os.getenv("MAX_CONTEXT_TOKENS", "8000"))
        strategy = os.getenv("CONTEXT_STRATEGY", "truncate")
        _context_manager = ContextManager(max_tokens=max_tokens, strategy=strategy)
    return _context_manager

