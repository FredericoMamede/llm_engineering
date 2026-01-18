"""
Model Manager - LLM client management.

Manages connections to multiple LLM providers and provides
unified interface for model access.
"""

import os
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)


class ModelManager:
    """Manages LLM clients for multiple providers."""
    
    def __init__(self):
        """Initialize model manager and load API keys."""
        self.clients = {}
        self._initialize_clients()
    
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
        
        # Ollama (always available if running locally)
        self.clients["ollama"] = OpenAI(
            api_key="ollama",
            base_url="http://localhost:11434/v1"
        )
    
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
        elif any(x in model_lower for x in ["llama", "qwen", "deepseek"]):
            return self.clients.get("ollama")
        else:
            # Try OpenAI as default
            return self.clients.get("openai")
