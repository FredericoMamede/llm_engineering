from typing import Optional, Dict, Any
from openai import OpenAI, APIError, APIConnectionError
import time
from utils import count_tokens
from config import (
    OLLAMA_BASE_URL, get_model_name, get_openai_cost,
    MAX_RETRIES, RETRY_BASE_DELAY, RETRY_MAX_DELAY, RETRYABLE_ERROR_CODES
)
from logger import logger

# Week 1 learning: OpenAI-compatible endpoints enable unified interface
# Both OpenAI and Ollama use the same API format, so we can use one client library
class ModelClient:
    """
    Unified interface for OpenAI and Ollama models.
    
    Model abstraction enables easy switching between providers.
    Both OpenAI and Ollama use OpenAI-compatible endpoints, so the same client library works.
    This allows side-by-side model comparison and easy experimentation.
    """
    
    def __init__(self, provider: str, model_name: Optional[str] = None):
        """
        Initialize model client for specified provider.
        
        Week 1 learning: OpenAI-compatible endpoints mean we can use the same client
        for both OpenAI (cloud) and Ollama (local). Just change the base_url.
        
        Args:
            provider: 'openai' or 'ollama'
            model_name: Optional model name (uses defaults if not provided)
        
        Raises:
            ValueError: If provider is unknown
        """
        self.provider = provider
        self.model = get_model_name(provider, model_name)
        
        if provider == 'openai':
            # Standard OpenAI client (uses OPENAI_API_KEY from environment)
            self.client = OpenAI()
            logger.debug(f"Initialized OpenAI client with model: {self.model}")
        elif provider == 'ollama':
            # Ollama uses OpenAI-compatible endpoint with custom base_url
            # Week 1 learning: This is the key insight - same API, different endpoint
            self.client = OpenAI(
                base_url=OLLAMA_BASE_URL,
                api_key='ollama'  # Ollama doesn't require real auth, but API expects it
            )
            logger.debug(f"Initialized Ollama client with model: {self.model}")
        else:
            raise ValueError(f"Unknown provider: {provider}. Use 'openai' or 'ollama'")
    
    def _should_retry(self, error: Exception) -> bool:
        """
        Determine if an error is retryable.
        
        Week 1 learning: Not all errors should be retried.
        Only transient errors (rate limits, server errors) should trigger retries.
        
        Args:
            error: Exception that occurred
        
        Returns:
            True if error is retryable, False otherwise
        """
        if isinstance(error, APIConnectionError):
            return True  # Connection errors are often transient
        
        if isinstance(error, APIError):
            # Check if error code indicates retryable condition
            error_code = getattr(error, 'code', None) or str(error).lower()
            return any(code in error_code for code in RETRYABLE_ERROR_CODES)
        
        return False
    
    def _call_with_retry(
        self,
        system_prompt: str,
        user_prompt: str,
        stream: bool = False,
        response_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make LLM call with retry logic and exponential backoff.
        
        Week 1 learning: Retry logic is essential for production reliability.
        Transient errors (rate limits, network issues) often succeed on retry.
        
        Args:
            system_prompt: System message for the LLM
            user_prompt: User message for the LLM
            stream: Whether to stream response
            response_format: Optional response format ('json_object' for JSON mode)
        
        Returns:
            Dict with content, tokens, latency, and cost (if applicable)
        """
        last_error = None
        
        for attempt in range(MAX_RETRIES):
            try:
                return self._make_api_call(system_prompt, user_prompt, stream, response_format)
            except Exception as e:
                last_error = e
                
                # Check if error is retryable
                if not self._should_retry(e) or attempt == MAX_RETRIES - 1:
                    # Not retryable or last attempt - raise immediately
                    raise
                
                # Calculate exponential backoff delay
                delay = min(RETRY_BASE_DELAY * (2 ** attempt), RETRY_MAX_DELAY)
                logger.warning(
                    f"API call failed (attempt {attempt + 1}/{MAX_RETRIES}): {type(e).__name__}. "
                    f"Retrying in {delay:.1f}s..."
                )
                time.sleep(delay)
        
        # Should never reach here, but just in case
        raise last_error or RuntimeError("Unexpected retry loop exit")
    
    def _make_api_call(
        self,
        system_prompt: str,
        user_prompt: str,
        stream: bool = False,
        response_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Internal method to make a single API call (no retry logic).
        
        Args:
            system_prompt: System message for the LLM
            user_prompt: User message for the LLM
            stream: Whether to stream response
            response_format: Optional response format ('json_object' for JSON mode)
        
        Returns:
            Dict with content, tokens, latency, and cost
        """
        start_time = time.time()
        
        # Week 1 learning: Count input tokens for cost awareness
        # Input = system prompt + user prompt
        input_text = system_prompt + "\n\n" + user_prompt
        input_tokens = count_tokens(input_text, self.model) or 0
        
        try:
            # Week 1 learning: JSON mode forces structured output (OpenAI feature)
            # This makes parsing more reliable by guaranteeing valid JSON
            # Note: JSON mode only works with non-streaming for OpenAI models
            api_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }
            
            # Add response_format if specified (JSON mode)
            if response_format == 'json_object' and self.provider == 'openai':
                # JSON mode requires explicit instruction in system prompt
                # and response_format parameter
                api_params["response_format"] = {"type": "json_object"}
            
            if stream:
                # Week 1 learning: Streaming requires collecting chunks
                # Use list-based concatenation (O(n)) instead of string += (O(n²))
                # Note: JSON mode doesn't work with streaming, so we skip it here
                collected_chunks = []
                
                api_params["stream"] = True
                stream_response = self.client.chat.completions.create(**api_params)
                
                # Collect all chunks
                for chunk in stream_response:
                    chunk_text = chunk.choices[0].delta.content or ''
                    if chunk_text:  # Only append non-empty chunks
                        collected_chunks.append(chunk_text)
                
                # Week 1 learning: Join once at end (efficient O(n) operation)
                content = ''.join(collected_chunks)
                
                # Streaming responses don't always include usage info
                # Count output tokens manually if not available
                output_tokens = count_tokens(content, self.model) or 0
                
            else:
                # Non-streaming: get full response at once
                # JSON mode works with non-streaming requests
                response = self.client.chat.completions.create(**api_params)
                
                content = response.choices[0].message.content
                
                # Week 1 learning: Try to get token usage from response (more accurate)
                # Some providers (like OpenAI) include usage info in response
                if hasattr(response, 'usage') and response.usage:
                    output_tokens = response.usage.completion_tokens or 0
                    # Update input tokens if response provides more accurate count
                    if response.usage.prompt_tokens:
                        input_tokens = response.usage.prompt_tokens
                else:
                    # Fallback: count manually (for providers that don't include usage)
                    output_tokens = count_tokens(content, self.model) or 0
            
            # Week 1 learning: Handle empty response edge case
            # Prevents downstream errors in pipeline
            if not content:
                raise RuntimeError(f"{self.model} returned empty response")
            
            latency = time.time() - start_time
            
            # Calculate cost for OpenAI models
            cost = None
            if self.provider == 'openai':
                cost = get_openai_cost(self.model, input_tokens, output_tokens)
            
            return {
                'content': content,
                'tokens': {
                    'input': input_tokens,
                    'output': output_tokens,
                    'total': input_tokens + output_tokens
                },
                'latency': latency,
                'cost': cost
            }
            
        except APIConnectionError as e:
            # Week 1 learning: Specific exception handling provides better error context
            # Connection errors are different from API errors - user needs different hints
            raise ConnectionError(
                f"Connection failed to {self.model} provider. "
                f"Error: {e}. "
                "Hint: Check your internet connection or API endpoint (for Ollama, ensure it's running)."
            ) from e
        except APIError as e:
            # API-level errors: auth, rate limits, model availability, etc.
            raise RuntimeError(
                f"API error with {self.model}. "
                f"Error: {e}. "
                "Hint: Check your API key, rate limits, or model availability."
            ) from e
        except Exception as e:
            # Catch-all for unexpected errors
            raise RuntimeError(
                f"Unexpected error calling {self.model}: {type(e).__name__}: {e}"
            ) from e
    
    def call(
        self,
        system_prompt: str,
        user_prompt: str,
        stream: bool = False,
        response_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make LLM call with error handling, token tracking, latency measurement, and retry logic.
        
        Week 1 learning: This method abstracts away provider differences.
        Returns structured response with content, tokens, latency, and cost for comparison.
        
        Args:
            system_prompt: System message for the LLM
            user_prompt: User message for the LLM
            stream: Whether to stream response (real-time chunks)
            response_format: Optional response format ('json_object' for JSON mode)
        
        Returns:
            Dict with:
                - 'content': Generated text content
                - 'tokens': Dict with 'input' and 'output' token counts
                - 'latency': Time taken in seconds
                - 'cost': Estimated cost in USD (for OpenAI models, None for others)
        
        Raises:
            ConnectionError: If connection to API fails
            RuntimeError: If API returns an error
        """
        logger.debug(f"Making API call to {self.model} (stream={stream}, format={response_format})")
        return self._call_with_retry(system_prompt, user_prompt, stream, response_format)