"""
Ollama Models Adapter

Supports local models via Ollama API.
Requires Ollama to be running locally.
"""

import requests
from typing import Optional

from .base import BaseModel, GenerationConfig, ModelResponse


# Common Ollama models 
# These are suggestions 
OLLAMA_MODELS = {
    "llama3_2_3b": "llama3.2:3b",
    "llama3_2": "llama3.2",
    "llama3_1_8b": "llama3.1:8b",
    "mistral": "mistral",
    "mistral_7b": "mistral:7b",
    "phi3": "phi3",
    "qwen2_5": "qwen2.5:7b",
    "gemma2": "gemma2:2b",
    "tinyllama": "tinyllama",
}


class OllamaModel(BaseModel):
    """
    Ollama local model adapter.
    
    Design decisions:
    - Uses Ollama's REST API (assumes Ollama is running)
    - Default base URL is localhost:11434
    - Handles connection errors gracefully
    - Maps GenerationConfig to Ollama API format
    """
    
    def __init__(
        self,
        model_name: str,
        base_url: str = "http://localhost:11434"
    ):
        """
        Args:
            model_name: Ollama model name (e.g., "llama3.2:3b")
            base_url: Ollama API base URL (default: localhost:11434)
        """
        super().__init__(model_name, "ollama")
        self.base_url = base_url.rstrip("/")
        self._api_url = f"{self.base_url}/api/generate"
    
    def is_loaded(self) -> bool:
        # Ollama models are managed by Ollama service
        # Check if Ollama is accessible
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False
    
    def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None
    ) -> ModelResponse:
        """Generate text using Ollama API"""
        if config is None:
            config = GenerationConfig()
        
        try:
            # Ollama API format
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,  # Get complete response
                "options": {
                    "temperature": config.temperature,
                    "num_predict": config.max_tokens,
                }
            }
            
            if config.top_p is not None:
                payload["options"]["top_p"] = config.top_p
            
            if config.seed is not None:
                payload["options"]["seed"] = config.seed
            
            if config.stop_sequences:
                payload["options"]["stop"] = config.stop_sequences
            
            response = requests.post(
                self._api_url,
                json=payload,
                timeout=300  # 5 minute timeout for long generations
            )
            response.raise_for_status()
            
            result = response.json()
            generated_text = result.get("response", "")
            
            return ModelResponse(
                text=generated_text,
                model_name=self.model_name,
                provider="ollama",
                metadata={
                    "eval_count": result.get("eval_count"),
                    "prompt_eval_count": result.get("prompt_eval_count"),
                    "total_duration": result.get("total_duration"),
                }
            )
            
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                f"Cannot connect to Ollama at {self.base_url}. "
                f"Is Ollama running? Start it with: ollama serve"
            )
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(
                f"Ollama API error for '{self.model_name}': {str(e)}. "
                f"Make sure the model is pulled: ollama pull {self.model_name}"
            )
        except Exception as e:
            raise RuntimeError(
                f"Ollama generation failed for '{self.model_name}': {str(e)}"
            ) from e
