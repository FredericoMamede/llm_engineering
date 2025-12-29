import tiktoken
from typing import Dict, Any, Optional
from urllib.parse import urlparse
import re
from config import MIN_TEXT_LENGTH
from logger import logger

def count_tokens(text: Optional[str], model: str = 'gpt-4o-mini') -> Optional[int]:
    """
    Count tokens in text using tiktoken.
    
    Token awareness is crucial for cost management and context window limits.
    Different models use different tokenizers, so we specify the model to get the right encoding.
    
    For models not recognized by tiktoken (e.g., local Ollama models), falls back to cl100k_base
    encoding which provides a reasonable approximation.
    
    Args:
        text: Text to count tokens for (can be None)
        model: Model name (default: gpt-4o-mini)
    
    Returns:
        Number of tokens in text, or None if text is None
    """
    if text is None:
        return None
    
    try:
        # Try to get encoding for the specific model
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback for models not recognized by tiktoken (e.g., local Ollama models)
        # Use cl100k_base as a reasonable approximation (used by GPT-4, GPT-3.5)
        encoding = tiktoken.get_encoding("cl100k_base")
        logger.debug(f"Model '{model}' not recognized by tiktoken. Using 'cl100k_base' encoding.")
    
    return len(encoding.encode(text))

def validate_text_input(text: Optional[str], min_length: Optional[int] = None) -> None:
    """
    Validate text input using fail-fast approach.
    
    Week 1 learning: Validate early to prevent wasted API calls and get clear error messages.
    This follows the "fail fast" pattern - catch invalid input before expensive operations.
    
    Args:
        text: Text to validate (can be None)
        min_length: Minimum required length (defaults to MIN_TEXT_LENGTH from config)
    
    Raises:
        ValueError: If text is None or too short
    """
    if min_length is None:
        min_length = MIN_TEXT_LENGTH
    
    if text is None:
        raise ValueError("Text input cannot be None")

    stripped_text = text.strip()
    if not stripped_text:
        raise ValueError("Text input cannot be empty")
    if len(stripped_text) < min_length:
        raise ValueError(f"Text must be at least {min_length} characters")

def validate_url(url: str) -> None:
    """
    Validate URL format using standard library (urllib.parse).
    
    Week 1 learning: Use standard library for validation instead of regex or LLM calls.
    This is faster, more reliable, and doesn't waste API costs. Fail-fast pattern applies here too.
    
    Args:
        url: URL string to validate
    
    Raises:
        ValueError: If URL format is invalid
    
    Examples:
        >>> validate_url("https://example.com")  # Valid
        >>> validate_url("not-a-url")  # Raises ValueError
    """
    if not url or not url.strip():
        raise ValueError("URL cannot be empty or whitespace only")
    
    try:
        result = urlparse(url.strip())
        
        # Check for required components (scheme and domain are mandatory)
        if not result.scheme:
            raise ValueError(f"URL missing scheme (http/https): {url}")
        
        if not result.netloc:
            raise ValueError(f"URL missing domain: {url}")
        
        # Only allow http/https for security (no file://, javascript:, etc.)
        if result.scheme not in ['http', 'https']:
            raise ValueError(f"URL scheme must be http or https, got: {result.scheme}")
        
        # Handle ports in domain (e.g., "example.com:8080" -> validate "example.com")
        netloc = result.netloc
        if ':' in netloc:
            netloc = netloc.split(':')[0]

        # Validate domain structure: must have TLD (dot), no leading/trailing dots
        if '.' not in netloc or netloc.startswith('.') or netloc.endswith('.'):
            raise ValueError(f"Invalid domain format: {result.netloc}")     

    except ValueError:
        # Re-raise our custom ValueError
        raise
    except Exception as e:
        # Catch any unexpected parsing errors
        raise ValueError(f"Invalid URL format: {url}. Error: {e}")

def format_output_json(results: Dict[str, Any]) -> str:
    """
    Format pipeline results as JSON.
    
    Week 1 learning: Structured output (JSON) is easier to parse programmatically.
    Useful for integration with other tools or automated processing.
    
    Args:
        results: Dictionary with all pipeline results
    
    Returns:
        JSON-formatted string
    """
    import json
    # Create clean output dict (remove None values for cleaner JSON)
    output = {k: v for k, v in results.items() if v is not None and k != 'errors'}
    return json.dumps(output, indent=2, ensure_ascii=False)


def format_output(
    results: Dict[str, Any],
    tone: Optional[str] = None,
    include_separators: bool = True
) -> str:
    """
    Format pipeline results into clean, readable output.
    
    Args:
        results: Dictionary with summary, bullets, rewritten, translated, etc.
        tone: Tone used for rewriting (for display in header)
        include_separators: Whether to include section separators
    
    Returns:
        Formatted string ready for console or file output
    
    Example:
        >>> results = {
        ...     'summary': 'This is a summary',
        ...     'bullets': '* Point 1\n* Point 2',
        ...     'rewritten': 'Rewritten text'
        ... }
        >>> print(format_output(results, tone='professional'))
    """
    output_parts = []
    separator = "\n" + ("=" * 60 + "\n" if include_separators else "\n")
    
    # Summary section
    if results.get('summary'):
        output_parts.append("**Summary**\n")
        summary = results['summary'].strip()
        # Ensure it ends with proper punctuation if it's a sentence
        if summary and not summary.endswith(('.', '!', '?', ':', ';')):
            if len(summary) > 20 and not any(char in summary for char in [':', ';', '-']):
                summary += ':'
        output_parts.append(f"{summary}\n")
        if include_separators:
            output_parts.append(separator)
    
    # Key Points section
    if results.get('bullets'):
        output_parts.append("\n**Key Points**\n")
        bullets = results['bullets']
        
        # Handle different bullet formats (LLM might return string or list)
        if isinstance(bullets, str):
            # If it's already formatted as a string, parse line by line
            bullet_lines = bullets.strip().split('\n')
            for line in bullet_lines:
                line = line.strip()
                if line:
                    # Normalize bullet format: remove any existing bullets, always use *
                    # This handles cases where LLM returns "- Point" or "• Point" or "* Point"
                    line = line.lstrip('*-• ')  # Remove common bullet chars
                    output_parts.append(f"* {line}\n")
        elif isinstance(bullets, list):
            # If it's a list, format each item
            for bullet in bullets:
                bullet = str(bullet).strip()
                if bullet:
                    output_parts.append(f"* {bullet}\n")
        output_parts.append("\n")
        if include_separators:
            output_parts.append(separator)
    
    # Rewritten section
    if results.get('rewritten'):
        tone_label = f" ({tone.title()} Tone)" if tone else ""
        output_parts.append(f"**Rewritten{tone_label}**\n\n")
        rewritten = results['rewritten'].strip()
        # Format as blockquote for readability
        output_parts.append(f"> {rewritten}\n")
        if include_separators:
            output_parts.append(separator)
    
    # Translated section (optional)
    if results.get('translated'):
        output_parts.append("\n**Translated**\n\n")
        translated = results['translated'].strip()
        output_parts.append(f"{translated}\n")
    
    # Join all parts and clean up extra newlines
    output = "\n".join(output_parts)
    # Remove excessive blank lines (more than 2 consecutive)
    output = re.sub(r'\n{3,}', '\n\n', output)
    
    return output.strip()