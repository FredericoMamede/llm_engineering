"""
Configuration constants and settings for LLM Playground.

Week 1 learning: Centralizing configuration makes the codebase more maintainable.
All magic numbers and constants live here, making it easy to adjust behavior.
"""
import os
from typing import Dict, Optional

# ============================================================================
# API Configuration
# ============================================================================

# OpenAI-compatible endpoint for Ollama
OLLAMA_BASE_URL = "http://localhost:11434/v1"

# Default model names per provider
DEFAULT_MODELS = {
    'openai': 'gpt-4o-mini',
    'ollama': 'llama3.2'
}

# OpenAI pricing per 1M tokens (as of 2024)
# Source: https://openai.com/pricing
OPENAI_PRICING = {
    'gpt-4o-mini': {
        'input': 0.15,   # $0.15 per 1M input tokens
        'output': 0.60   # $0.60 per 1M output tokens
    },
    'gpt-4o': {
        'input': 2.50,
        'output': 10.00
    },
    'gpt-4-turbo': {
        'input': 10.00,
        'output': 30.00
    },
    'gpt-3.5-turbo': {
        'input': 0.50,
        'output': 1.50
    }
}

# ============================================================================
# Scraping Configuration
# ============================================================================

# Maximum content length for LLM processing (cost management)
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '2000'))

# HTTP request timeout (seconds)
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '10'))

# Playwright navigation timeout (milliseconds)
PLAYWRIGHT_TIMEOUT = int(os.getenv('PLAYWRIGHT_TIMEOUT', '30000'))

# Browser headers to mimic real browser (prevents blocking)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

# ============================================================================
# Prompt Configuration
# ============================================================================

# Content truncation limits for cost management
ANALYSIS_MAX_CHARS = 3000
TRANSFORM_MAX_CHARS = 4000
TRANSLATION_MAX_CHARS = 3000

# ============================================================================
# API Retry Configuration
# ============================================================================

# Retry settings for API calls
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
RETRY_BASE_DELAY = float(os.getenv('RETRY_BASE_DELAY', '1.0'))  # seconds
RETRY_MAX_DELAY = float(os.getenv('RETRY_MAX_DELAY', '10.0'))  # seconds

# Retryable error codes (transient errors that might succeed on retry)
RETRYABLE_ERROR_CODES = [
    'rate_limit_exceeded',
    'server_error',
    'timeout',
    'internal_error'
]

# ============================================================================
# Output Configuration
# ============================================================================

# Supported output formats
OUTPUT_FORMATS = ['text', 'json', 'markdown']

# Default output format
DEFAULT_OUTPUT_FORMAT = 'text'

# ============================================================================
# Language Support
# ============================================================================

# Language code to name mapping for translation prompts
LANGUAGE_NAMES: Dict[str, str] = {
    'nl': 'Dutch',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ja': 'Japanese',
    'zh': 'Chinese',
    'ko': 'Korean',
    'ru': 'Russian',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'pl': 'Polish',
    'tr': 'Turkish',
    'sv': 'Swedish',
    'da': 'Danish',
    'no': 'Norwegian',
    'fi': 'Finnish'
}

# ============================================================================
# Validation Configuration
# ============================================================================

# Minimum text length for processing
MIN_TEXT_LENGTH = int(os.getenv('MIN_TEXT_LENGTH', '10'))

# ============================================================================
# Helper Functions
# ============================================================================

def get_model_name(provider: str, model_name: Optional[str] = None) -> str:
    """
    Get model name for provider, using default if not specified.
    
    Args:
        provider: 'openai' or 'ollama'
        model_name: Optional custom model name
    
    Returns:
        Model name to use
    """
    if model_name:
        return model_name
    return DEFAULT_MODELS.get(provider, DEFAULT_MODELS['openai'])


def get_openai_cost(model: str, input_tokens: int, output_tokens: int) -> Optional[float]:
    """
    Calculate estimated cost for OpenAI API call.
    
    Week 1 learning: Cost awareness is crucial for production LLM applications.
    This helps track and optimize spending.
    
    Args:
        model: Model name (e.g., 'gpt-4o-mini')
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
    
    Returns:
        Estimated cost in USD, or None if model pricing not available
    """
    if model not in OPENAI_PRICING:
        return None
    
    pricing = OPENAI_PRICING[model]
    input_cost = (input_tokens / 1_000_000) * pricing['input']
    output_cost = (output_tokens / 1_000_000) * pricing['output']
    
    return input_cost + output_cost


def get_language_name(lang_code: str) -> str:
    """
    Get full language name from code.
    
    Args:
        lang_code: Language code (e.g., 'nl')
    
    Returns:
        Full language name (e.g., 'Dutch') or uppercase code if not found
    """
    return LANGUAGE_NAMES.get(lang_code.lower(), lang_code.upper())

