"""
OpenAI Models Adapter

Supports OpenAI chat models via API.
No local model loading required - all inference via API.
"""

import os
from typing import Optional
from openai import OpenAI

from .base import BaseModel, GenerationConfig, ModelResponse


# OpenAI models suitable for synthetic data generation
OPENAI_MODELS = {
    "gpt_4o": "gpt-4o",
    "gpt_4o_mini": "gpt-4o-mini",
    "gpt_4_turbo": "gpt-4-turbo",
    "gpt_4": "gpt-4",
    "gpt_3_5_turbo": "gpt-3.5-turbo",
}


class OpenAIModel(BaseModel):
    """
    OpenAI API model adapter.
    
    Design decisions:
    - No local loading (all via API)
    - Handles API key from environment or parameter
    - Maps GenerationConfig to OpenAI API parameters
    - Always uses chat format (OpenAI's standard)
    """
    
    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        api_key: Optional[str] = None
    ):
        """
        Args:
            model_name: OpenAI model identifier (e.g., "gpt-4o-mini")
            api_key: OpenAI API key (or use OPENAI_API_KEY env var)
        """
        super().__init__(model_name, "openai")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key parameter"
            )
        
        self._client = OpenAI(api_key=self.api_key)
    
    def is_loaded(self) -> bool:
        # OpenAI models are always "loaded" (API-based)
        return True
    
    def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None
    ) -> ModelResponse:
        """Generate text using OpenAI API"""
        if config is None:
            config = GenerationConfig()
        
        try:
            # OpenAI uses chat format
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                seed=config.seed,
                stop=config.stop_sequences,
            )
            
            generated_text = response.choices[0].message.content
            
            return ModelResponse(
                text=generated_text,
                model_name=self.model_name,
                provider="openai",
                metadata={
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    },
                    "finish_reason": response.choices[0].finish_reason,
                }
            )
            
        except Exception as e:
            raise RuntimeError(
                f"OpenAI API call failed for '{self.model_name}': {str(e)}"
            ) from e
