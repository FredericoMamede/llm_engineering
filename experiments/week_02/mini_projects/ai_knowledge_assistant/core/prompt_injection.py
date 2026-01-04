"""
Prompt injection protection: detect and sanitize user input.

Features:
- Prompt injection pattern detection
- Input sanitization
- System prompt isolation
- User input escaping
"""

import re
from typing import List, Optional, Tuple

from core.logger import get_logger

logger = get_logger(__name__)


# Common prompt injection patterns
INJECTION_PATTERNS = [
    # Direct instruction attempts
    r"(?i)(ignore|forget|disregard).*(previous|above|system|instructions)",
    r"(?i)(you are|act as|pretend to be|roleplay as)",
    r"(?i)(system|assistant):\s*(you|your|ignore)",
    
    # Instruction injection
    r"(?i)(new instructions|updated instructions|revised instructions)",
    r"(?i)(override|replace|change).*(system|instructions|prompt)",
    
    # Context manipulation
    r"(?i)(start over|begin again|reset|clear)",
    r"(?i)(previous conversation|earlier messages).*(ignore|forget)",
    
    # Jailbreak attempts
    r"(?i)(jailbreak|bypass|hack|exploit)",
    r"(?i)(developer mode|admin mode|debug mode)",
    
    # Role confusion
    r"(?i)(you're|you are).*(now|currently).*(a|an|the)",
    r"(?i)(switch|change).*(role|persona|identity)",
    
    # Output manipulation
    r"(?i)(output|respond|answer).*(as|in|using).*(format|style|language)",
    r"(?i)(don't|do not).*(say|mention|include|use)",
    
    # Encoding tricks
    r"&lt;|&gt;|&amp;",  # HTML entities
    r"\\x[0-9a-f]{2}",  # Hex encoding
    r"\\u[0-9a-f]{4}",  # Unicode encoding
]


def detect_injection(user_input: str) -> Tuple[bool, List[str]]:
    """
    Detect potential prompt injection attempts.
    
    Args:
        user_input: User input text to check
    
    Returns:
        (is_injection, detected_patterns)
    """
    if not user_input:
        return False, []
    
    detected = []
    
    for pattern in INJECTION_PATTERNS:
        matches = re.findall(pattern, user_input)
        if matches:
            detected.append(pattern)
    
    is_injection = len(detected) > 0
    
    if is_injection:
        logger.warning(
            "Potential prompt injection detected",
            extra={
                "pattern_count": len(detected),
                "input_length": len(user_input),
                "patterns": detected[:3],  # Log first 3 patterns
            },
        )
    
    return is_injection, detected


def sanitize_input(user_input: str, strict: bool = False) -> str:
    """
    Sanitize user input to prevent prompt injection.
    
    Args:
        user_input: User input to sanitize
        strict: If True, escape all special characters; if False, only escape suspicious patterns
    
    Returns:
        Sanitized input
    """
    if not user_input:
        return ""
    
    # Check for injection patterns
    is_injection, patterns = detect_injection(user_input)
    
    if not is_injection and not strict:
        # No suspicious patterns, return as-is
        return user_input
    
    # Sanitize: escape newlines and control characters
    sanitized = user_input
    
    # Replace newlines with spaces (prevents multi-line injection)
    sanitized = sanitized.replace("\n", " ").replace("\r", " ")
    
    # Remove control characters
    sanitized = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", sanitized)
    
    # Escape HTML entities
    sanitized = sanitized.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    # If injection detected, add warning marker
    if is_injection:
        logger.warning(
            "Sanitized user input due to injection patterns",
            extra={
                "original_length": len(user_input),
                "sanitized_length": len(sanitized),
                "pattern_count": len(patterns),
            },
        )
        # Add a marker that input was sanitized (for debugging)
        sanitized = f"[SANITIZED] {sanitized}"
    
    return sanitized


def escape_for_prompt(user_input: str) -> str:
    """
    Escape user input for safe inclusion in prompts.
    
    Args:
        user_input: User input to escape
    
    Returns:
        Escaped input safe for prompt inclusion
    """
    if not user_input:
        return ""
    
    # Basic escaping: wrap in clear delimiters
    escaped = user_input
    
    # Replace any existing delimiters
    escaped = escaped.replace("```", "'''")
    escaped = escaped.replace("---", "---")
    
    # Clear boundaries
    escaped = f"\n---USER INPUT START---\n{escaped}\n---USER INPUT END---\n"
    
    return escaped


def validate_input(user_input: str, max_length: int = 50000) -> Tuple[bool, Optional[str]]:
    """
    Validate user input for safety and size.
    
    Args:
        user_input: User input to validate
        max_length: Maximum allowed length
    
    Returns:
        (is_valid, error_message)
    """
    if not user_input or not user_input.strip():
        return False, "Input cannot be empty"
    
    if len(user_input) > max_length:
        return False, f"Input too long (max {max_length} characters)"
    
    # Check for injection
    is_injection, patterns = detect_injection(user_input)
    if is_injection and len(patterns) >= 3:
        # Multiple patterns detected - likely injection
        return False, "Input contains suspicious patterns that may be a security risk"
    
    return True, None


def prepare_safe_user_input(user_input: str, sanitize: bool = True) -> str:
    """
    Prepare user input for safe use in prompts.
    
    This is the main function to use when processing user input.
    
    Args:
        user_input: Raw user input
        sanitize: Whether to sanitize the input
    
    Returns:
        Safe user input ready for prompt inclusion
    """
    if not user_input:
        return ""
    
    # Validate
    is_valid, error = validate_input(user_input)
    if not is_valid:
        logger.warning(f"Input validation failed: {error}")
        # Still return input, but log the issue
        # In production, you might want to reject invalid input
    
    # Sanitize if requested
    if sanitize:
        sanitized = sanitize_input(user_input, strict=False)
        # Use escaped version for extra safety
        return escape_for_prompt(sanitized)
    
    return escape_for_prompt(user_input)

