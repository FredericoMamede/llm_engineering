from typing import Optional, Dict, Any
from openai import OpenAI, APIError, APIConnectionError
import time
from utils import count_tokens

# Week 1 learning: OpenAI-compatible endpoints enable unified interface
# Both OpenAI and Ollama use the same API format, so we can use one client library
OLLAMA_BASE_URL = "http://localhost:11434/v1"


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
        if provider == 'openai':
            # Standard OpenAI client (uses OPENAI_API_KEY from environment)
            self.client = OpenAI()
            self.model = model_name or 'gpt-4o-mini'
        elif provider == 'ollama':
            # Ollama uses OpenAI-compatible endpoint with custom base_url
            # Week 1 learning: This is the key insight - same API, different endpoint
            self.client = OpenAI(
                base_url=OLLAMA_BASE_URL,
                api_key='ollama'  # Ollama doesn't require real auth, but API expects it
            )
            self.model = model_name or 'llama3.2'
        else:
            raise ValueError(f"Unknown provider: {provider}. Use 'openai' or 'ollama'")
    
    def call(
        self,
        system_prompt: str,
        user_prompt: str,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Make LLM call with error handling, token tracking, and latency measurement.
        
        Week 1 learning: This method abstracts away provider differences.
        Returns structured response with content, tokens, and latency for comparison.
        
        Args:
            system_prompt: System message for the LLM
            user_prompt: User message for the LLM
            stream: Whether to stream response (real-time chunks)
        
        Returns:
            Dict with:
                - 'content': Generated text content
                - 'tokens': Dict with 'input' and 'output' token counts
                - 'latency': Time taken in seconds
        
        Raises:
            ConnectionError: If connection to API fails
            RuntimeError: If API returns an error
        """
        start_time = time.time()
        
        # Week 1 learning: Count input tokens for cost awareness
        # Input = system prompt + user prompt
        input_text = system_prompt + "\n\n" + user_prompt
        input_tokens = count_tokens(input_text, self.model) or 0
        
        try:
            if stream:
                # Week 1 learning: Streaming requires collecting chunks
                # Use list-based concatenation (O(n)) instead of string += (O(n²))
                collected_chunks = []
                
                stream_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    stream=True
                )
                
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
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                
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
            
            return {
                'content': content,
                'tokens': {
                    'input': input_tokens,
                    'output': output_tokens,
                    'total': input_tokens + output_tokens
                },
                'latency': latency
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