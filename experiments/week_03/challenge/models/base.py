"""
Base Model Interface for Synthetic Data Generation

This module defines a common interface that all model providers must implement.
This allows the generation logic to work with any model without knowing the provider.

Design Decision:
- Adapter pattern: Each provider (HF, OpenAI, Ollama) implements this interface
- Generation logic depends on abstraction, not concrete implementations
- Easy to add new providers without changing core generation code
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class GenerationConfig:
    """Configuration for text generation across all providers"""
    temperature: float = 0.7
    max_tokens: int = 512
    top_p: Optional[float] = None
    seed: Optional[int] = None
    stop_sequences: Optional[List[str]] = None


@dataclass
class ModelResponse:
    """Standardized response from any model provider"""
    text: str
    model_name: str
    provider: str
    metadata: Optional[Dict[str, Any]] = None


class BaseModel(ABC):
    """
    Abstract base class for all model providers.
    
    All model implementations (HF, OpenAI, Ollama) must inherit from this
    and implement the generate() method.
    
    Why this pattern:
    - Decouples generation logic from specific providers
    - Enables easy model switching in UI and experiments
    - Makes testing easier (can mock this interface)
    """
    
    def __init__(self, model_name: str, provider: str):
        """
        Args:
            model_name: Identifier for the model (e.g., "meta-llama/Llama-3.2-3B-Instruct")
            provider: Provider name (e.g., "huggingface", "openai", "ollama")
        """
        self.model_name = model_name
        self.provider = provider
        self._model = None  # Lazy loading - only load when needed
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None
    ) -> ModelResponse:
        """
        Generate text from a prompt.
        
        Args:
            prompt: Input text prompt
            config: Generation parameters (temperature, max_tokens, etc.)
            
        Returns:
            ModelResponse with generated text and metadata
            
        Raises:
            RuntimeError: If model fails to generate (provider-specific errors)
        """
        pass
    
    @abstractmethod
    def is_loaded(self) -> bool:
        """Check if model is currently loaded in memory"""
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model='{self.model_name}', provider='{self.provider}')"
