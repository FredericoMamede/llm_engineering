"""
Model Manager - LLM client management.

Manages connections to multiple LLM providers and provides
unified interface for model access.

Separates model capability (what we support) from availability
(what the user can actually use).
"""

import os
import yaml
from typing import Optional, Dict, List, Tuple
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)


class ModelManager:
    """
    Manages LLM clients for multiple providers.
    
    Separates capability (supported models) from availability
    (models user can actually use based on credentials).
    
    Note: Anthropic and Gemini providers are accessed via OpenAI-compatible
    adapters for interface uniformity. This is an intentional design choice
    and does not imply native SDK usage.
    """
    
    def __init__(self):
        """Initialize model manager and load API keys."""
        self.clients = {}
        self.model_profiles = self._load_model_profiles()
        self._initialize_clients()
    
    def _load_model_profiles(self) -> Dict:
        """Load model profiles from YAML configuration."""
        config_path = Path(__file__).parent.parent / "config" / "model_prompt_profiles.yaml"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}
    
    def _initialize_clients(self):
        """Initialize all available clients based on API keys."""
        # OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.clients["openai"] = OpenAI(api_key=openai_key)
        
        # Anthropic
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            self.clients["anthropic"] = OpenAI(
                api_key=anthropic_key,
                base_url="https://api.anthropic.com/v1/"
            )
        
        # Google (Gemini)
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            self.clients["google"] = OpenAI(
                api_key=google_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
        
        # Ollama (check if running locally)
        if self._check_ollama_available():
            self.clients["ollama"] = OpenAI(
                api_key="ollama",
                base_url="http://localhost:11434/v1"
            )
        
        # Hugging Face (gated models)
        hf_token = os.getenv("HUGGINGFACE_TOKEN")
        if hf_token:
            # Use Hugging Face Inference API (OpenAI-compatible endpoint)
            self.clients["huggingface"] = OpenAI(
                api_key=hf_token,
                base_url="https://api-inference.huggingface.co/v1"
            )
    
    def _check_ollama_available(self) -> bool:
        """Check if Ollama is running locally."""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=1)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_client(self, model_name: str) -> Optional[OpenAI]:
        """
        Get appropriate client for a model.
        
        Args:
            model_name: Model identifier
        
        Returns:
            OpenAI client instance or None
        """
        model_lower = model_name.lower()
        
        # Map model to provider
        if "claude" in model_lower:
            return self.clients.get("anthropic")
        elif "gpt" in model_lower:
            return self.clients.get("openai")
        elif "gemini" in model_lower:
            return self.clients.get("google")
        elif "meta-llama/llama-4" in model_lower or "llama-4" in model_lower:
            # LLaMA-4 is gated via Hugging Face, not Ollama
            return self.clients.get("huggingface")
        elif any(x in model_lower for x in ["llama", "qwen", "deepseek", "mixtral", "mistral", "gemma"]):
            return self.clients.get("ollama")
        else:
            # Try OpenAI as default
            return self.clients.get("openai")
    
    def get_model_profile(self, model_name: str) -> Optional[Dict]:
        """
        Get model profile for a given model name.
        
        Args:
            model_name: Model identifier
        
        Returns:
            Model profile dict or None
        """
        model_lower = model_name.lower()
        
        # Find matching profile
        for profile_key, profile_data in self.model_profiles.items():
            if profile_key == "adaptation_rules" or profile_key == "generic":
                continue
            
            models = profile_data.get("models", [])
            if any(model_lower in m.lower() or m.lower() in model_lower for m in models):
                return profile_data
        
        # Return generic profile if no match
        return self.model_profiles.get("generic")
    
    def check_model_availability(self, model_name: str) -> Tuple[bool, str]:
        """
        Check if a model is available for use.
        
        Args:
            model_name: Model identifier
        
        Returns:
            (is_available: bool, reason: str)
        """
        profile = self.get_model_profile(model_name)
        if not profile:
            return False, "Model profile not found"
        
        # Check API key requirement
        requires_api_key = profile.get("requires_api_key", False)
        if requires_api_key:
            required_env_var = profile.get("required_env_var")
            if required_env_var and not os.getenv(required_env_var):
                return False, f"Requires API key: {required_env_var}"
        
        # Check local runtime requirement
        local_runtime_required = profile.get("local_runtime_required", False)
        if local_runtime_required:
            provider = profile.get("provider", "ollama")
            if provider == "ollama" and not self._check_ollama_available():
                return False, "Ollama not running locally"
        
        # Check Hugging Face gated access requirement
        provider = profile.get("provider", "")
        if provider == "huggingface":
            required_env_var = profile.get("required_env_var")
            if required_env_var and not os.getenv(required_env_var):
                return False, f"Requires gated Hugging Face access: {required_env_var}"
        
        # Check if client is available
        client = self.get_client(model_name)
        if not client:
            provider = profile.get("provider", "unknown")
            return False, f"Client not available for provider: {provider}"
        
        return True, "Available"
    
    def get_all_supported_models(self) -> List[Dict]:
        """
        Get all supported models with availability status.
        
        Returns:
            List of dicts with model info and availability
        """
        models = []
        
        for profile_key, profile_data in self.model_profiles.items():
            if profile_key in ["adaptation_rules", "generic"]:
                continue
            
            profile_models = profile_data.get("models", [])
            provider = profile_data.get("provider", "unknown")
            requires_api_key = profile_data.get("requires_api_key", False)
            required_env_var = profile_data.get("required_env_var")
            
            for model_name in profile_models:
                is_available, reason = self.check_model_availability(model_name)
                
                models.append({
                    "name": model_name,
                    "profile": profile_key,
                    "provider": provider,
                    "requires_api_key": requires_api_key,
                    "required_env_var": required_env_var,
                    "available": is_available,
                    "unavailable_reason": reason if not is_available else None
                })
        
        return models