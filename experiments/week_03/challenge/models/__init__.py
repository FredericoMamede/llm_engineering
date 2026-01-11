"""
Model Providers for Synthetic Data Generation

Exports:
- BaseModel: Abstract interface all models implement
- HuggingFaceModel: HF models (gated + open)
- OpenAIModel: OpenAI API models
- OllamaModel: Local Ollama models
- Model factory functions
"""

from .base import BaseModel, GenerationConfig, ModelResponse
from .hf_models import HuggingFaceModel, HF_MODELS, get_all_hf_models, get_model_by_key
from .openai_models import OpenAIModel, OPENAI_MODELS
from .ollama_models import OllamaModel, OLLAMA_MODELS


def create_model(
    provider: str,
    model_name: str,
    **kwargs
) -> BaseModel:
    """
    Factory function to create model instances.
    
    Args:
        provider: "huggingface", "openai", or "ollama"
        model_name: Model identifier
        **kwargs: Provider-specific arguments
        
    Returns:
        BaseModel instance
        
    Example:
        model = create_model("huggingface", "meta-llama/Llama-3.2-3B-Instruct")
        model = create_model("openai", "gpt-4o-mini", api_key="...")
        model = create_model("ollama", "llama3.2:3b")
    """
    provider = provider.lower()
    
    if provider == "huggingface" or provider == "hf":
        return HuggingFaceModel(model_name, **kwargs)
    elif provider == "openai":
        return OpenAIModel(model_name, **kwargs)
    elif provider == "ollama":
        return OllamaModel(model_name, **kwargs)
    else:
        raise ValueError(
            f"Unknown provider: {provider}. "
            f"Supported: 'huggingface', 'openai', 'ollama'"
        )


__all__ = [
    "BaseModel",
    "GenerationConfig",
    "ModelResponse",
    "HuggingFaceModel",
    "OpenAIModel",
    "OllamaModel",
    "create_model",
    "HF_MODELS",
    "OPENAI_MODELS",
    "OLLAMA_MODELS",
    "get_all_hf_models",
    "get_model_by_key",
]
