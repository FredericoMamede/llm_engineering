"""
Multi-provider model client setup.

This module initializes clients for various LLM providers:
- OpenAI
- Anthropic
- Google (Gemini)
- Grok (x.ai)
- Groq
- Ollama (local)
- OpenRouter
"""

import os
from typing import Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)


class ModelClients:
    """Container for all model clients."""

    def __init__(self):
        self.openai: Optional[OpenAI] = None
        self.anthropic: Optional[OpenAI] = None
        self.gemini: Optional[OpenAI] = None
        self.grok: Optional[OpenAI] = None
        self.groq: Optional[OpenAI] = None
        self.ollama: Optional[OpenAI] = None
        self.openrouter: Optional[OpenAI] = None

    def initialize(self):
        """Initialize all available clients based on API keys."""
        openai_api_key = os.getenv("OPENAI_API_KEY")
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        google_api_key = os.getenv("GOOGLE_API_KEY")
        grok_api_key = os.getenv("GROK_API_KEY")
        groq_api_key = os.getenv("GROQ_API_KEY")
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

        if openai_api_key:
            self.openai = OpenAI(api_key=openai_api_key)

        if anthropic_api_key:
            self.anthropic = OpenAI(
                api_key=anthropic_api_key,
                base_url="https://api.anthropic.com/v1/",
            )

        if google_api_key:
            self.gemini = OpenAI(
                api_key=google_api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            )

        if grok_api_key:
            self.grok = OpenAI(
                api_key=grok_api_key,
                base_url="https://api.x.ai/v1",
            )

        if groq_api_key:
            self.groq = OpenAI(
                api_key=groq_api_key,
                base_url="https://api.groq.com/openai/v1",
            )

        if openrouter_api_key:
            self.openrouter = OpenAI(
                api_key=openrouter_api_key,
                base_url="https://openrouter.ai/api/v1",
            )

        # Ollama is always available if running locally
        self.ollama = OpenAI(
            api_key="ollama",
            base_url="http://localhost:11434/v1",
        )


def get_model_clients() -> ModelClients:
    """Get initialized model clients."""
    clients = ModelClients()
    clients.initialize()
    return clients


def get_client_for_model(model_name: str, clients: ModelClients) -> Optional[OpenAI]:
    """Get the appropriate client for a given model name."""
    model_to_client = {
        "gpt-5": clients.openai,
        "gpt-5-nano": clients.openai,
        "claude-sonnet-4-5-20250929": clients.anthropic,
        "claude-3-5-haiku-latest": clients.anthropic,
        "gemini-2.5-pro": clients.gemini,
        "gemini-2.5-flash-lite": clients.gemini,
        "grok-4": clients.grok,
        "grok-4-fast-non-reasoning": clients.grok,
        "openai/gpt-oss-120b": clients.groq,
        "qwen2.5-coder": clients.ollama,
        "deepseek-coder-v2": clients.ollama,
        "gpt-oss:20b": clients.ollama,
        "qwen/qwen3-coder-30b-a3b-instruct": clients.openrouter,
    }

    for key, client in model_to_client.items():
        if key in model_name.lower():
            return client

    return None
